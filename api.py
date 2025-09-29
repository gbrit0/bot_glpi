from flask import Flask, request, jsonify, Response, make_response
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import mysql.connector
from datetime import datetime
import json
from threading import Thread
import queue

load_dotenv(override=True) 

pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="botGLPI",
    pool_size=10,
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
    # print(f"data.get('author').get('id'): {data.get('author').get('id')}")
    # print(f"type(data.get('author').get('id')): {type(data.get('author').get('id'))}")

    return jsonify("OK"), 200

@app.route('/webhook', methods=['POST'])
def handle_glpi_webhook():
    # print('entrou em /webhook')
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid JSON or no JSON received"}), 400

    print(f"{datetime.now()}\t/webhook\taction: {data.get('ticket').get('action')}\tticket_id: {data.get('ticket').get('id')}")
    print(f"\ndata: {data}\n")
    try:
        if data.get('ticket').get('observergroups') == "notificacao_protheus" and (data.get('ticket').get('action') == "Novo chamado" or data.get('ticket').get('action') == "Chamado solucionado") and data.get('author').get('id') in ['2', '183', '233', '329', '137']:
            print("entrou no if de notificação_protheus")
            # Inicia a thread e responde imediatamente
            thread = Thread(target=send_update_protheus_async, args=(data,))
            thread.start()

            return jsonify("Request received"), 200

        elif data.get('ticket').get('lastupdater') != data.get('author').get('name') or data.get('ticket').get('action') == "Novo chamado":
            # if data.get('author').get('mobile') == '556281321017' or data.get('author').get('mobile') == '556286342844':
            send_message(data)
        elif data.get('ticket').get('lastupdater') == data.get('author').get('name'): # Mensagem do autor Enviar para o técnico
            # print(f"------ {data.get('author').get('name')} ------\n")
            print(f"{data}\n")
            id_chamado = data.get('ticket').get('id')
            nome_tecnico, telefone_tecnico = busca_dados_tecnico(id_chamado)
            mensagem_do_autor(nome_tecnico, telefone_tecnico, data)

            # return jsonify("No message sent, last updater is the same as author."), 200


    except KeyError as e:
        return jsonify({"error": f"Missing key: {e}"}), 400
    

    return jsonify("received_data"), 200

@app.route('/answers', methods=['POST'])
def handle_user_list_response():
    print("handle_user_list_response\n")
    try:
        data = request.get_json()
        print(f'data: {data}\n')
        # action = data.get('data').get('message').get('listResponseMessage').get('contextInfo')['quotedMessage']['listMessage'].get('title').replace("*", "").replace("_","").lower()
        print(f"{datetime.now()}\t/answers\taction: {data.get('ticket').get('action')}\tticket_id: {data.get('data').get('message').get('listResponseMessage').get('singleSelectReply').get('selectedRowId')}")
        # print(data)
        
        if data is None:
            print("Data is None")
            return jsonify({"error": "Invalid JSON or no JSON received"}), 400

        if data.get('data').get('messageType') != 'listResponseMessage':
            print("Message Type <> listResponseMessage")
            return jsonify("received_data"), 200

        id_mensagem = data.get('data').get('message').get('listResponseMessage').get('contextInfo').get('stanzaId')
        # print(f"id_mensagem: {id_mensagem}")

        sql = f"""SELECT id_mensagem FROM respostas WHERE id_mensagem = '{id_mensagem}'"""
        with pool.get_connection() as con:
            with con.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchone()
                
                if not result:
                    send_users_ticket_validation(data)
                    values = [str(data.get('data').get('key').get('id')), str(id_mensagem), '', str(datetime.now()), str(data.get('data').get('message').get('listResponseMessage').get('title'))]
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
        raise e
    
        
    
    return jsonify("received_data"), 200

def send_update_protheus(data):
    sql = f"SELECT CONCAT(u.firstname, ' ', u.realname) AS nome, u.mobile FROM glpi_groups_users AS gu LEFT JOIN glpi_users AS u ON u.id = gu.users_id WHERE gu.groups_id = '{os.getenv('GLPI_USER_GROUP_ID')}';"
    with pool.get_connection() as con:
        with con.cursor() as cursor:
            cursor.execute(sql)
            usuarios = cursor.fetchall()

    for usuario in usuarios:
        if data.get('ticket').get('action') == "Novo chamado":
            payload = {
                "number": f"{usuario[1]}",
                "text":f"""Olá, {usuario[0]}!\n\n{clean_html(data.get('ticket').get('content'))}""",
                "delay": 2000,
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
            # data.get('ticket').get('action') == "Chamado solucionado"
            payload = {
                "number": f"{usuario[1]}",
                "text":f"""Olá, {usuario[0]}!\n\n{clean_html(data.get('ticket').get('solution').get('description'))}""",
                "delay": 2000,
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

        enqueue_chat(payload)

def init_glpi_api_session():
   glpiApiHeaders = {
        "Authorization": f"{os.getenv('GLPI_AUTH')}",
        "App-Token": f"{os.getenv('GLPI_APP_TOKEN')}",
        "Content-Type": "application/json"
    }

   url = f"{os.getenv('GLPI_API_BASE_URL')}/initSession/"

   response = requests.request("GET", url, headers=glpiApiHeaders)
   return response.json().get('session_token')

def kill_glpi_api_session(session_token):
   headers = {
      "Session-Token": f"{session_token}",
      "App-Token": f"{os.getenv('GLPI_APP_TOKEN')}",
      "Content-Type": "application/json"
   }

   url = f"{os.getenv('GLPI_API_BASE_URL')}/killSession"

   response = requests.request("GET", url, headers=headers)

def send_users_ticket_validation(data):
    print("entrou em send_users_ticket_validation\n")
    session_token = init_glpi_api_session()
    # print(f"Sessão GLPI iniciada. session_token: {session_token}\n")
    ticket_id = data.get('data').get('message').get('listResponseMessage').get('singleSelectReply').get('selectedRowId')
    resposta_chamado = data.get('data').get('message').get('listResponseMessage').get('title')

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
    
    # response = requests.request("PUT", url, headers=headers, json=payload)
    try:
        response = requests.request("PUT", url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()  # levanta erro para códigos 4xx/5xx
    except requests.Timeout:
        print("Erro: timeout ao tentar acessar a API.")
    except requests.RequestException as e:
        print(f"Erro de requisição: {e}")
    

    kill_glpi_api_session(session_token)

def clean_html(texto):
    texto = texto.replace("<br>", "\n").replace("<li>", "   * ")
    clean = BeautifulSoup(texto, "html.parser")
    return clean.get_text()

def mensagem_do_autor(nome_tecnico, telefone_tecnico, data):
    payload = {
                "number": f"{telefone_tecnico}",
                "text":f"""*_RESPOSTA DO AUTOR_*\n\nOlá, {nome_tecnico}!\n\n{data.get('author').get('name')}, autor do chamado nº {data.get('ticket').get('id')} - {data.get('ticket').get('title')} enviou uma nova mensagem. Acesse o GLPI para visualizar: {data.get('ticket').get('url')}""",
                "delay": 2000,
                "linkPreview": True,
                "mentionsEveryOne": False,
                "quoted": {
                    "key": {
                        "fromMe": True,
                        "type":'Mensagem do autor',
                        "id": ""
                    }
                }
            }
    enqueue_chat(payload)

def send_message(data):
    # print("Entrou em send_message")
    match data.get('ticket').get('action'):
        
        case 'Novo chamado':
            payload = {
                "number": f"{data.get('author').get('mobile')}",
                "text":f"""*_NOVO CHAMADO_*\n\nOlá, {data.get('author').get('name')}!\n\nRecebemos seu chamado nº {data.get('ticket').get('id')} - {data.get('ticket').get('title')}:\n\n\tAs atualizações em seu chamado serão enviadas em seu Whatsapp.\n\nPara acompanhar acesse o link: {data.get('ticket').get('url')}""",
                "delay": 2000,
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

            enqueue_chat(payload)

        case 'Novo acompanhamento':
            if clean_html(data.get('ticket').get('solution').get('approval').get('description')) != 'Solução aprovada':
                if data.get('documents') != '':
                    text = f"""*_NOVO ACOMPANHAMENTO_*\n\nOlá, {data.get('author').get('name')}!\n\n{data.get('ticket').get('action')} em seu chamado nº {data.get('ticket').get('id')} - {data.get('ticket').get('title')}:\n\n\t*{data.get('ticket').get('solution').get('approval').get('author')}:* {clean_html(data.get('ticket').get('solution').get('approval').get('description'))}\n\nHá um documento associado a essa atualização, para acompanhar acesse o link: {data.get('ticket').get('url')}"""
                else:
                    text = f"""*_NOVO ACOMPANHAMENTO_*\n\nOlá, {data.get('author').get('name')}!\n\n{data.get('ticket').get('action')} em seu chamado nº {data.get('ticket').get('id')} - {data.get('ticket').get('title')}:\n\n\t*{data.get('ticket').get('solution').get('approval').get('author')}:* {clean_html(data.get('ticket').get('solution').get('approval').get('description'))}\n\nPara acompanhar acesse o link: {data.get('ticket').get('url')}"""
                payload = {
                    "number": f"{data.get('author').get('mobile')}",
                    "text":f"{text}",
                    "delay": 2000,
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

                enqueue_chat(payload)
        
        case 'Pesquisa de satisfação':
            print(f"Pesquisa de satisfação")
            text = f"""*_PESQUISA DE SATISFAÇÃO_*\n\nOlá, {data.get('author').get('name')}!\n\nSeu chamado nº {data.get('ticket').get('id')} - {data.get('ticket').get('title')}, foi fechado e a pesquisa de satisfação já pode ser respondida.\n\nPara responder acesse o link: {data.get('ticket').get('satisfaction').get('url')}"""
            payload = {
                "number": f"{data.get('author').get('mobile')}",
                "text":f"{text}",
                "delay": 2000,
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

            try:
                enqueue_chat(payload)
                register_ticket_satisfaction(data.get('ticket').get('id'))
            except Exception as e:
                print(f"{datetime.now()}\terro ao enviar mensagem de pesquisa de satisfação: {e}")
            
        case "Chamado solucionado":
            text = f"""*_CHAMADO SOLUCIONADO_*\n\nOlá, {data.get('author').get('name')}!\n\nSeu chamado nº {data.get('ticket').get('id')} - {data.get('ticket').get('title')}, foi foi solucionado!\n\n\t*{data.get('ticket').get('solution').get('author')}:* {clean_html(data.get('ticket').get('solution').get('description'))}\n\nPara aceitar ou negar a solução acesse o link:\n{data.get('ticket').get('url')}"""
            payload = {
                "number": f"{data.get('author').get('mobile')}",
                "text":f"{text}",
                "delay": 2000,
                "linkPreview": True,
                "mentionsEveryOne": False,
                "quoted": {
                    "key": {
                        "fromMe": True,
                        "type":'Chamado solucionado',
                        "id": ""
                    }
                }
            }
            # thread = Thread(target=send_ticket_solution_async, args=(payload,))
            # thread.start()
            # send_ticket_solution(payload)
            enqueue_chat(payload)
            return jsonify("Request received"), 200

        case _:
            
            payload = {
                "number": f"{data.get('author').get('mobile')}",
                "text":f"""*_ATUALIZAÇÃO DE UM CHAMADO_*\n\nOlá, {data.get('author').get('name')}!\n\n{data.get('ticket').get('lastupdater')} atualizou seu chamado nº {data.get('ticket').get('id')} - {data.get('ticket').get('title')}\n\n\t*status:* {data.get('ticket').get('status')}\n\nPara acompanhar acesse o link: {data.get('ticket').get('url')}""",
                "delay": 2000,
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
    
            enqueue_chat(payload)
    # print(response.text)

def chat_worker():
    print("chat_worker iniciado!")
    while True:
        payload = chat_queue.get()
        print(f"Processando payload na fila: {payload}")
        try:
            start_chat(payload)
        except Exception as e:
            print(f"Erro no chat_worker: {e}")
        finally:
            chat_queue.task_done()

def enqueue_chat(payload):
    print(f"Enfileirando payload: {payload}")
    chat_queue.put(payload)

import json

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
    # print(f"response post evolution: {data}\n")

    if response.status_code == 201:
        values = [str(data.get('key').get('id')), str(payload.get('number')), str(datetime.now()), str(payload.get('quoted').get('key').get('type')), str(payload.get('text'))]
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
        values = [str(data.get('key').get('id')), str(payload.get('number')), str(datetime.now()), str(payload.get('quoted').get('key').get('type')), json.dumps(payload.get('sections'), ensure_ascii=False)]
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

def register_ticket_satisfaction(ticketId):
    print(f"entrou em register_ticket_satisfaction com ticketId: {ticketId}")
    with pool.get_connection() as con:
        with con.cursor() as cursor:
            sql="""
            INSERT INTO `u629942907_glpi`.`glpi_itilsolutions` (itemtype, items_id, solutiontypes_id, content,`date_creation`, users_id) 
            VALUES ('Ticket', %s, 0, 'Pesquisa de satisfação enviada!', now(), 265);
            """
            try:
                cursor.execute(sql, (ticketId,))
                con.commit()
                
            except mysql.connector.Error as e:
                print(f"{datetime.now()}\terro de conexao MySQL: {e}")
            except Exception as e:
                print(f"{datetime.now()}\terro: {e}")

def busca_dados_tecnico(ticketId):
    query = f"""
    SELECT 
        CONCAT(TRIM(tec.firstname), ' ', TRIM(tec.realname)) AS atribuido,
        TRIM(tec.mobile) as telefone
    FROM
        glpi_tickets AS t
            LEFT JOIN
        glpi_tickets_users AS gtu ON t.id = gtu.tickets_id AND gtu.type = '2'
            LEFT JOIN
        glpi_users AS tec ON gtu.users_id = tec.id
    WHERE
        t.id = %s
    """
    with pool.get_connection() as con:
        with con.cursor() as cursor:
            cursor.execute(query, (ticketId,))
            result = cursor.fetchone()
            if result:
                return result


chat_queue = queue.Queue()

worker_thread = Thread(target=chat_worker, daemon=True)
worker_thread.start()

if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=52001, debug=True)
