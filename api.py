from flask import Flask, request, jsonify, Response, make_response
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import mysql.connector
from datetime import datetime
import json

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_glpi_webhook():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Invalid JSON or no JSON received"}), 400

    print(f"Received data: {data}")

    try:
        if data['ticket']['lastupdater'] != data['author']['name'] or data['ticket']['action'] == "Novo chamado":
            sendMessage(data)
    except KeyError as e:
        return jsonify({"error": f"Missing key: {e}"}), 400

    return jsonify({"received_data": data}), 200


@app.route('/answers', methods=['POST'])
def handle_user_list_response():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid JSON or no JSON received"}), 400

    if data['data']['messageType'] == 'listResponseMessage':
        id_mensagem = data['data']['message']['listResponseMessage']['contextInfo']['stanzaId']

        sql = f"""SELECT id_mensagem FROM respostas WHERE id_mensagem = '{id_mensagem}'"""
        with pool.get_connection() as con:
            with con.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchone()
                
                if not result:
                    send_users_ticket_validation(data)
                    values = [str(data['data']['key']['id']), str(id_mensagem), '', str(datetime.now()), str(data['data']['message']['listResponseMessage']['title'])]
                    sql = f"""INSERT INTO respostas (`id_resposta`, `id_mensagem`, `conteudo`, `data_hora`, `tipo`)
                    VALUES (%s, %s, %s, %s, %s)"""

                    try:
                        cursor.execute(sql, values)
                        con.commit()
                        
                    except mysql.connector.Error as e:
                        print(f"erro de conexao MySQL: {e}")

        
    
    return jsonify({"received_data": data}), 200


def initGlpiApiSession():
   glpiApiHeaders = {
        "Authorization": f"{os.getenv('GLPI_AUTH')}",
        "App-Token": f"{os.getenv('GLPI_APP_TOKEN')}",
        "Content-Type": "application/json"
    }

   url = f"{os.getenv('GLPI_API_BASE_URL')}/initSession/"

   response = requests.request("GET", url, headers=glpiApiHeaders)
   return response.json()['session_token']

def killGlpiApiSession(session_token):
   headers = {
      "Session-Token": f"{session_token}",
      "App-Token": f"{os.getenv('GLPI_APP_TOKEN')}",
      "Content-Type": "application/json"
   }

   url = f"{glpiApiBaseUrl}/killSession"

   response = requests.request("GET", url, headers=headers)

def send_users_ticket_validation(data):
    session_token = initGlpiApiSession()

    ticket_id = data['data']['message']['listResponseMessage']['singleSelectReply']['selectedRowId']
    resposta_chamado = data['data']['message']['listResponseMessage']['title']

    if resposta_chamado == 'Sim':
        payload = {
            "input":{
                "id":f"{ticket_id}",
                "status":6
            }
        }
    else:
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

    url = f"{glpiApiBaseUrl}/Ticket/{ticket_id}"
    
    response = requests.request("PUT", url, headers=headers, json=payload)
    # print(response.json())

    killGlpiApiSession(session_token)


def cleanHtml(texto):
    texto = texto.replace("<br>", "\n").replace("<li>", "   * ")
    clean = BeautifulSoup(texto, "html.parser")
    return clean.get_text()

def sendMessage(data):
    match data['ticket']['action']:
        
        case 'Novo chamado':
            payload = {
                "number": f"{data['author']['mobile']}",
                "textMessage": {
                    "text":f"""*_NOVO CHAMADO_*\n\nOlá, {data['author']['name']}!\n\nRecebemos seu chamado nº {data['ticket']['id']} - {data['ticket']['title']}:\n\n\tAs atualizações em seu chamado serão enviadas em seu Whatsapp\n\nPara acompanhar acesse o link: {data['ticket']['url']}"""
                },
                "delay": 1200,
                "linkPreview": True,
                "mentionsEveryOne": False,
                "quoted": {
                    "key": {
                        "fromMe": True,
                        "type":'Novo chamado'
                    }
                }
            }

            startChat(payload)
    
            
        case "Chamado solucionado":

            payload = {
                "number": f"{data['author']['mobile']}",
                "ticke_id": f"{data['ticket']['id']}",
                "listMessage": {
                    "title": "*_CHAMADO SOLUCIONADO_*",
                    "description": f"""Olá, {data['author']['name']}!\n\nSeu chamado nº {data['ticket']['id']} foi solucionado!\n\n\t*{data['ticket']['solution']['author']}:* {cleanHtml(data['ticket']['solution']['description'])}\n""",
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
                    ]
                },
                "options": {
                    "delay": 1200,
                    "presence": "composing"
                },
                "quoted": {
                    "key": {
                        "fromMe": True,
                        "type":"Chamado solucionado"
                    }
                }
            }
            
            sendTicketSolution(payload)


        case _:
            
            payload = {
                "number": f"{data['author']['mobile']}",
                "textMessage": {
                    "text":f"""*_ATUALIZAÇÃO DE UM CHAMADO_*\n\nOlá, {data['author']['name']}!\n\n\t{data['ticket']['lastupdater']} atualizou seu chamado nº {data['ticket']['id']} - {data['ticket']['title']}\n\nPara acompanhar acesse o link: {data['ticket']['url']}"""
                },
                "delay": 1200,
                "linkPreview": True,
                "mentionsEveryOne": False,
                "quoted": {
                    "key": {
                        "fromMe": True,
                        "type":"Caso geral"
                    }
                }
            }
    
            startChat(payload)
    # print(response.text)

def updateMessage(session_token, evolutionApiBaseUrl):
    evolutionApiHeaders = {
        "apikey": f"{os.getenv('EVOLUTION_API_KEY')}",
        "Content-Type": "application/json"
    }
    # message_id = data['data']['key']['id']
    url = f"{evolutionApiBaseUrl}/chat/updateMessage/Glpi_GBR"

    payload = {
        "number":"556286342844",
        "text":f"""Olá, !\n\nSeu chamado nº  foi solucionado!\n\n\t*AUTOR:* ASDFASDFASDF\n""",
        "key":{
            "remoteJid":"556286342844@s.whatsapp.net",
            "fromMe": True,
            "id": f"<>"
        },
        "status": "SENT"
        
    }
    
    response = requests.request("PUT", url, json=payload, headers=evolutionApiHeaders)
    print(response.json())


def startChat(payload):
    url = f"{evolutionApiBaseUrl}/message/sendText/Glpi_GBR"

    response = requests.request("POST", url, json=payload, headers=evolutionApiHeaders)
    data = response.json()
    if response.status_code == 201:
        values = [str(data['key']['id']), str(payload['number']), str(datetime.now()), str(payload['quoted']['key']['type']), str(payload['textMessage']['text'])]
        with pool.get_connection() as con:
            with con.cursor() as cursor:
                sql=f"""INSERT INTO `glpi`.`mensagens` (`id_mensagem`, `destinatario`, `data_hora`, `tipo`, `conteudo`) 
                VALUES (%s, %s, %s, %s, %s);"""
                try:
                    cursor.execute(sql, values)
                    con.commit()
                    
                except mysql.connector.Error as e:
                    print(f"erro de conexao MySQL: {e}")             


def sendTicketSolution(payload):
    url = f"{evolutionApiBaseUrl}/message/sendList/Glpi_GBR"

    response = requests.request("POST", url, json=payload, headers=evolutionApiHeaders)
    data = response.json()
    # print(data)
    if response.status_code == 201:
        values = [str(data['key']['id']), str(payload['number']), str(datetime.now()), str(payload['quoted']['key']['type']), json.dumps(payload['listMessage'], ensure_ascii=False)]
        with pool.get_connection() as con:
            with con.cursor() as cursor:
                sql=f"""INSERT INTO `glpi`.`mensagens` (`id_mensagem`, `destinatario`, `data_hora`, `tipo`, `conteudo`) 
                VALUES (%s, %s, %s, %s, %s);"""
                try:
                    cursor.execute(sql, values)
                    con.commit()
                    
                except mysql.connector.Error as e:
                    print(f"erro de conexao MySQL: {e}")

if __name__ == '__main__':
    load_dotenv()
    evolutionApiHeaders = {
        "apikey": f"{os.getenv('EVOLUTION_API_KEY')}",
        "Content-Type": "application/json"
    }

    evolutionApiBaseUrl = os.getenv('EVOLUTION_API_BASE_URL')

    glpiApiBaseUrl = os.getenv('GLPI_API_BASE_URL')

    pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="botGLPI",
        pool_size=5,
        user=os.getenv('GLPI_MYSQL_USER'),
        password=os.getenv('GLPI_MYSQL_PASSWORD'),
        host=os.getenv('GLPI_MYSQL_HOST'),
        database=os.getenv('GLPI_MYSQL_DATABASE'),
        collation='utf8mb4_general_ci' # especificando o collation para evitar erro de codificação
    )
    

    app.run(host='0.0.0.0', port=5000, debug=True)
