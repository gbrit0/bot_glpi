from flask import Flask, request, jsonify, Response, make_response
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_glpi_webhook():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Invalid JSON or no JSON received"}), 400

    print(f"Received data: {data}")

    try:
        if data['ticket']['lastupdater'] != data['author']['name']:
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
        print(f"Received data: {data}")
    
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


    killGlpiApiSession(session_token)


def cleanHtml(texto):
    texto = texto.replace("<br>", "\n").replace("<li>", "   * ")
    clean = BeautifulSoup(texto, "html.parser")
    return clean.get_text()

def sendMessage(data):
    match data['ticket']['action']:
    
        case 'Novo acompanhamento':
            payload = {
                "number": f"{data['author']['mobile']}",
                "textMessage": {
                    "text":f"""*_NOVO ACOMPANHAMENTO_*\n\nOlá, {data['author']['name']}!\n\n{data['ticket']['action']} em seu chamado nº {data['ticket']['id']} - {data['ticket']['title']}:\n\n\t*{data['ticket']['solution']['approval']['author']}:* {cleanHtml(data['ticket']['solution']['approval']['description'])}\n\nPara acompanhar acesse o link: {data['ticket']['url']}"""
                },
                "delay": 1200,
                "linkPreview": True,
                "mentionsEveryOne": False,
                "quoted": {
                    "key": {
                        "fromMe": True
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
                        "fromMe": True
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
                        "fromMe": True
                    }
                }
            }
    
            startChat(payload)
    # print(response.text)

def startChat(payload):
    url = f"{evolutionApiBaseUrl}/message/sendText/Glpi_GBR"

    response = requests.request("POST", url, json=payload, headers=evolutionApiHeaders)

def sendTicketSolution(payload):
    url = f"{evolutionApiBaseUrl}/message/sendList/Glpi_GBR"

    response = requests.request("POST", url, json=payload, headers=evolutionApiHeaders)
    # print(response)

if __name__ == '__main__':
    load_dotenv()
    evolutionApiHeaders = {
        "apikey": f"{os.getenv('EVOLUTION_API_KEY')}",
        "Content-Type": "application/json"
    }

    evolutionApiBaseUrl = os.getenv('EVOLUTION_API_BASE_URL')

    glpiApiBaseUrl = os.getenv('GLPI_API_BASE_URL')
    app.run(host='0.0.0.0', port=5000, debug=True)