from flask import Flask, request, jsonify, Response, make_response
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import mysql.connector
from datetime import datetime
import json
from threading import Thread

load_dotenv(override=True) 

pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="botGLPI",
    pool_size=5,
    user=os.getenv('GLPI_MYSQL_USER'),
    password=os.getenv('GLPI_MYSQL_PASSWORD'),
    host=os.getenv('GLPI_MYSQL_HOST'),
    port=os.getenv('GLPI_MYSQL_PORT'),
    database=os.getenv('GLPI_MYSQL_DATABASE'),
    collation='utf8mb4_general_ci' # especificando o collation para evitar erro de codificação
)

app = Flask(__name__)

def send_update_protheus_async(data):
    try:
        send_update_protheus(data)
    except Exception as e:
        print(f"Erro ao processar send_update_protheus: {e}")

def send_ticket_solution_async(data):
    try:
        send_ticket_solution(data)
    except Exception as e:
        print(f"Erro ao processar send_ticket_solution: {e}")


@app.route('/', methods=['GET', 'POST'])
def tudo():
    data = request.get_json()
    print(data)
    # print(f"data['author']['id']: {data['author']['id']}")
    # print(f"type(data['author']['id']): {type(data['author']['id'])}")

    return jsonify("OK"), 200

@app.route('/webhook', methods=['POST'])
def handle_glpi_webhook():
    # print('entrou em /webhook')
    data = request.get_json()
    print(data)
    # print(f'request: {request}')
    if data is None:
        return jsonify({"error": "Invalid JSON or no JSON received"}), 400

    print(f"{datetime.now()}\t/webhook\taction: {data['ticket']['action']}\tticket_id: {data['ticket']['id']}")
    try:
        if data['ticket'].get('observergroups') == "notificacao_protheus" and (data['ticket']['action'] == "Novo chamado" or data['ticket']['action'] == "Chamado solucionado") and data['author']['id'] in ['2', '183', '233', '329', '137']:
            print("entrou no if de notificação_protheus")
            # Inicia a thread e responde imediatamente
            thread = Thread(target=send_update_protheus_async, args=(data,))
            thread.start()

            return jsonify("Request received"), 200

        elif data['ticket']['lastupdater'] != data['author']['name'] or data['ticket']['action'] == "Novo chamado":
            # if data['author']['mobile'] == '556281321017' or data['author']['mobile'] == '556286342844':
            send_message(data)
    except KeyError as e:
        return jsonify({"error": f"Missing key: {e}"}), 400
    

    return jsonify("received_data"), 200

@app.route('/answers', methods=['POST'])
def handle_user_list_response():
    # print("handle_user_list_response\n")
    try:
        data = request.get_json()
        # print(data)
        # action = data['data']['message']['listResponseMessage']['contextInfo']['quotedMessage']['listMessage']['title'].replace("*", "").replace("_","").lower()
        # print(f"{datetime.now()}\t/answers\taction: {data['ticket']['action']}\tticket_id: {data['data']['message']['listResponseMessage']['singleSelectReply']['selectedRowId']}")
        
        if data is None:
            return jsonify({"error": "Invalid JSON or no JSON received"}), 400

        if data['data']['messageType'] != 'listResponseMessage':
            return jsonify("received_data"), 200

        id_mensagem = data['data']['message']['listResponseMessage']['contextInfo']['stanzaId']
        # print(f"id_mensagem: {id_mensagem}")

        sql = f"""SELECT id_mensagem FROM respostas WHERE id_mensagem = '{id_mensagem}'"""
        with pool.get_connection() as con:
            with con.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchone()
                
                if not result:
                    send_users_ticket_validation(data)
                    values = [str(data['data']['key']['id']), str(id_mensagem), '', str(datetime.now()), str(data['data']['message']['listResponseMessage']['title'])]
                    sql = f"""INSERT INTO u629942907_glpi.respostas (`id_resposta`, `id_mensagem`, `conteudo`, `data_hora`, `tipo`)
                    VALUES (%s, %s, %s, %s, %s)"""

                    try:
                        cursor.execute(sql, values)
                        con.commit()
                        
                    except mysql.connector.Error as e:
                        print(f"{datetime.now()}\terro de conexao MySQL: {e}")
                    except Exception as e:
                        print(f"{datetime.now()}\terro: {e}")
                    # finally:
                    #     exit()
    except Exception as e:
        print(e)
    
        
    
    return jsonify("received_data"), 200

def send_update_protheus(data):
    sql = f"SELECT CONCAT(u.firstname, ' ', u.realname) AS nome, u.mobile FROM glpi_groups_users AS gu LEFT JOIN glpi_users AS u ON u.id = gu.users_id WHERE gu.groups_id = '39';"
    with pool.get_connection() as con:
        with con.cursor() as cursor:
            cursor.execute(sql)
            usuarios = cursor.fetchall()

    for usuario in usuarios:
        if data['ticket']['action'] == "Novo chamado":
            payload = {
                "number": f"{usuario[1]}",
                "text":f"""Olá, {usuario[0]}!\n\n{clean_html(data['ticket']['content'])}""",
                "delay": 3000,
                "linkPreview": True,
                "mentionsEveryOne": False,
                "quoted": {
                    "key": {
                        "fromMe": True,
                        "type":'Atualização no Protheus',
                        "id": ""
                    }
                }
            }
        else:
            # data['ticket']['action'] == "Chamado solucionado"
            payload = {
                "number": f"{usuario[1]}",
                "text":f"""Olá, {usuario[0]}!\n\n{clean_html(data['ticket']['solution']['description'])}""",
                "delay": 3000,
                "linkPreview": True,
                "mentionsEveryOne": False,
                "quoted": {
                    "key": {
                        "fromMe": True,
                        "type":'Atualização no Protheus',
                        "id": ""
                    }
                }
            }

        start_chat(payload)

def init_glpi_api_session():
   glpiApiHeaders = {
        "Authorization": f"{os.getenv('GLPI_AUTH')}",
        "App-Token": f"{os.getenv('GLPI_APP_TOKEN')}",
        "Content-Type": "application/json"
    }

   url = f"{os.getenv('GLPI_API_BASE_URL')}/initSession/"

   response = requests.request("GET", url, headers=glpiApiHeaders)
   return response.json()['session_token']

def kill_glpi_api_session(session_token):
   headers = {
      "Session-Token": f"{session_token}",
      "App-Token": f"{os.getenv('GLPI_APP_TOKEN')}",
      "Content-Type": "application/json"
   }

   url = f"{os.getenv('GLPI_API_BASE_URL')}/killSession"

   response = requests.request("GET", url, headers=headers)

def send_users_ticket_validation(data):
    # print("entrou em send_users_ticket_validation\n")
    session_token = init_glpi_api_session()
    # print(f"Sessão GLPI iniciada. session_token: {session_token}\n")
    ticket_id = data['data']['message']['listResponseMessage']['singleSelectReply']['selectedRowId']
    resposta_chamado = data['data']['message']['listResponseMessage']['title']

    if resposta_chamado == 'Sim':
        # print("resposta_chamado == 'Sim'")
        payload = {
            "input":{
                "id":f"{ticket_id}",
                "status":6
            }
        }
    if resposta_chamado == "Não":
        payload = {
            "input":{
                "id":f"{ticket_id}",
                "status":2
            }
        }


    headers = {
      "Session-Token": f"{session_token}",
      "App-Token": f"{os.getenv('GLPI_APP_TOKEN')}",
      "Content-Type": "application/json"
   }

    url = f"{os.getenv('GLPI_API_BASE_URL')}/Ticket/{ticket_id}"
    
    response = requests.request("PUT", url, headers=headers, json=payload)
    # print(f'response da api glpipara o send_user_ticket_validation: {response.json()}\n')

    kill_glpi_api_session(session_token)

def clean_html(texto):
    texto = texto.replace("<br>", "\n").replace("<li>", "   * ")
    clean = BeautifulSoup(texto, "html.parser")
    return clean.get_text()

def send_message(data):
    match data['ticket']['action']:
        
        case 'Novo chamado':
            payload = {
                "number": f"{data['author']['mobile']}",
                "text":f"""*_NOVO CHAMADO_*\n\nOlá, {data['author']['name']}!\n\nRecebemos seu chamado nº {data['ticket']['id']} - {data['ticket']['title']}:\n\n\tAs atualizações em seu chamado serão enviadas em seu Whatsapp.\n\nPara acompanhar acesse o link: {data['ticket']['url']}""",
                "delay": 3000,
                "linkPreview": True,
                "mentionsEveryOne": False,
                "quoted": {
                    "key": {
                        "fromMe": True,
                        "type":'Novo chamado',
                        "id": ""
                    }
                }
            }

            start_chat(payload)

        case 'Novo acompanhamento':
            if clean_html(data['ticket']['solution']['approval']['description']) != 'Solução aprovada':
                if data['documents'] != '':
                    text = f"""*_NOVO ACOMPANHAMENTO_*\n\nOlá, {data['author']['name']}!\n\n{data['ticket']['action']} em seu chamado nº {data['ticket']['id']} - {data['ticket']['title']}:\n\n\t*{data['ticket']['solution']['approval']['author']}:* {clean_html(data['ticket']['solution']['approval']['description'])}\n\nHá um documento associado a essa atualização, para acompanhar acesse o link: {data['ticket']['url']}"""
                else:
                    text = f"""*_NOVO ACOMPANHAMENTO_*\n\nOlá, {data['author']['name']}!\n\n{data['ticket']['action']} em seu chamado nº {data['ticket']['id']} - {data['ticket']['title']}:\n\n\t*{data['ticket']['solution']['approval']['author']}:* {clean_html(data['ticket']['solution']['approval']['description'])}\n\nPara acompanhar acesse o link: {data['ticket']['url']}"""
                payload = {
                    "number": f"{data['author']['mobile']}",
                    "text":f"{text}",
                    "delay": 3000,
                    "linkPreview": True,
                    "mentionsEveryOne": False,
                    "quoted": {
                        "key": {
                            "fromMe": True,
                            "type":'Novo acompanhamento',
                            "id": ""
                        }
                    }
                }

                start_chat(payload)
        
        case 'Pesquisa de satisfação':
            print(f"Pesquisa de satisfação")
            text = f"""*_PESQUISA DE SATISFAÇÃO_*\n\nOlá, {data['author']['name']}!\n\nSeu chamado nº {data['ticket']['id']} - {data['ticket']['title']}, foi fechado e a pesquisa de satisfação já pode ser respondida.\n\nPara responder acesse o link: {data['ticket']['satisfaction']['url']}"""
            payload = {
                "number": f"{data['author']['mobile']}",
                "text":f"{text}",
                "delay": 3000,
                "linkPreview": True,
                "mentionsEveryOne": False,
                "quoted": {
                    "key": {
                        "fromMe": True,
                        "type":'Pesquisa de satisfação',
                        "id": ""
                    }
                }
            }

            start_chat(payload)
            
        case "Chamado solucionado":
            payload = {
                "number": f"{data['author']['mobile']}",
                "title": "*_CHAMADO SOLUCIONADO_*",
                "description": f"""Olá, {data['author']['name']}!\n\nSeu chamado nº {data['ticket']['id']} foi solucionado!\n\n\t*{data['ticket']['solution']['author']}:* {clean_html(data['ticket']['solution']['description'])}\n""",
                "buttonText": "Clique aqui para aceitar ou negar a solução",
                "footerText": f"Para acompanhar acesse o link:\n{data['ticket']['url']}",
                "sections": [
                    {
                        "title": "Aprovar solução:",
                        "rows": [
                            {
                                "title": "Sim",
                                "description": "A solução foi satisfatória.",
                                "rowId": f"{data['ticket']['id']}" # passando o ticketId para recuperar mais fácil na hora de enviar a aprovação
                            },
                            {
                                "title": "Não",
                                "description": "A solução não foi satisfatória.",
                                "rowId": f"{data['ticket']['id']}" # passando o ticketId para recuperar mais fácil na hora de enviar a aprovação
                            }
                        ]
                    }
                ],
                "quoted": {
                    "key": {
                        "fromMe": True,
                        "type":"Chamado solucionado",
                        "id": ""
                    }
                }
            }
            thread = Thread(target=send_ticket_solution_async, args=(payload,))
            thread.start()
            # send_ticket_solution(payload)
            return jsonify("Request received"), 200


        case _:
            
            payload = {
                "number": f"{data['author']['mobile']}",
                "text":f"""*_ATUALIZAÇÃO DE UM CHAMADO_*\n\nOlá, {data['author']['name']}!\n\n{data['ticket']['lastupdater']} atualizou seu chamado nº {data['ticket']['id']} - {data['ticket']['title']}\n\n\t*status:* {data['ticket']['status']}\n\nPara acompanhar acesse o link: {data['ticket']['url']}""",
                "delay": 3000,
                "linkPreview": True,
                "mentionsEveryOne": False,
                "quoted": {
                    "key": {
                        "fromMe": True,
                        "type":"Caso geral",
                        "id": ""
                    }
                }
            }
    
            start_chat(payload)
    # print(response.text)

def start_chat(payload):
    # print("Entrou em start_chat")
    url = f"{os.getenv('EVOLUTION_API_BASE_URL')}/message/sendText/{os.getenv('EVOLUTION_INSTANCE')}"

    response = requests.request(
        "POST", 
        url, 
        json=payload, 
        headers={
            "apikey": f"{os.getenv('EVOLUTION_API_KEY')}",
            "Content-Type": "application/json"
        }
    )
    
    data = response.json()
    # print(data)
    if response.status_code == 201:
        values = [str(data['key']['id']), str(payload['number']), str(datetime.now()), str(payload['quoted']['key']['type']), str(payload['text'])]
        with pool.get_connection() as con:
            # print("conectado na pool")
            with con.cursor() as cursor:
                # print("conectado no cursor")
                sql=f"""INSERT INTO `u629942907_glpi`.`mensagens` (`id_mensagem`, `destinatario`, `data_hora`, `tipo`, `conteudo`) 
                VALUES (%s, %s, %s, %s, %s);"""
                try:
                    cursor.execute(sql, values)
                    con.commit()
                    
                except mysql.connector.Error as e:
                    print(f"{datetime.now()}\terro de conexao MySQL: {e}")
                except Exception as e:
                    print(f"{datetime.now()}\terro: {e}")             

def send_ticket_solution(payload):
    # print("Entrou em send_ticket_solution")
    # print(payload)
    url = f"{os.getenv('EVOLUTION_API_BASE_URL')}/message/sendList/{os.getenv('EVOLUTION_INSTANCE')}"

    response = requests.request(
        "POST", 
        url, 
        json=payload, 
        headers={
            "apikey": f"{os.getenv('EVOLUTION_API_KEY')}",
            "Content-Type": "application/json"
        }
    )
    data = response.json()
    # print(data)
    if response.status_code == 201:
        values = [str(data['key']['id']), str(payload['number']), str(datetime.now()), str(payload['quoted']['key']['type']), json.dumps(payload['sections'], ensure_ascii=False)]
        with pool.get_connection() as con:
            with con.cursor() as cursor:
                sql=f"""INSERT INTO `u629942907_glpi`.`mensagens` (`id_mensagem`, `destinatario`, `data_hora`, `tipo`, `conteudo`) 
                VALUES (%s, %s, %s, %s, %s);"""
                try:
                    cursor.execute(sql, values)
                    con.commit()
                    
                except mysql.connector.Error as e:
                    print(f"{datetime.now()}\terro de conexao MySQL: {e}\n")
                except Exception as e:
                    print(f"{datetime.now()}\terro: {e}\n")

if __name__ == '__main__':
    
    evolutionApiHeaders = {
        "apikey": f"{os.getenv('EVOLUTION_API_KEY')}",
        "Content-Type": "application/json"
    }

    evolutionApiBaseUrl = os.getenv('EVOLUTION_API_BASE_URL')

    glpiApiBaseUrl = os.getenv('GLPI_API_BASE_URL')

    # pool = mysql.connector.pooling.MySQLConnectionPool(
    #     pool_name="botGLPI",
    #     pool_size=5,
    #     user=os.getenv('GLPI_MYSQL_USER'),
    #     password=os.getenv('GLPI_MYSQL_PASSWORD'),
    #     host=os.getenv('GLPI_MYSQL_HOST'),
    #     database=os.getenv('GLPI_MYSQL_DATABASE'),
    #     collation='utf8mb4_general_ci' # especificando o collation para evitar erro de codificação
    # )
    
    # with pool.get_connection() as con:
    #     with con.cursor() as cursor:
    #         print('conectado com sucesso na base de daos nova do glpi')
    app.run(host='0.0.0.0', port=52001, debug=True)
