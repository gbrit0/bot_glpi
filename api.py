from flask import Flask, request, jsonify, Response, make_response
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

headers = {
        "apikey": "07bknevdrycmun144k9plmh",
        "Content-Type": "application/json"
    }

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

    print(f"Received data: {data}")
    return jsonify({"received_data": data}), 200


def cleanHtml(texto):
    clean = BeautifulSoup(texto, "html.parser")
    return clean.get_text()

def sendMessage(data):
    match data['ticket']['action']:
    
        case 'Novo acompanhamento':
            payload = {
                        "number": f"{data['author']['mobile']}", # destinatário
                        "textMessage": {
                            "text":f"""*_NOVO ACOMPANHAMENTO_*
                            
Olá, {data['author']['name']}!
                            
{data['ticket']['action']} em seu chamado nº {data['ticket']['id']} - {data['ticket']['title']}:

    *{data['ticket']['solution']['approval']['author']}:* "{cleanHtml(data['ticket']['solution']['approval']['description'])}"

Para acompanhar acesse o link: {data['ticket']['url']}
                        """
                        },
                        "delay": 1200,
                        "quoted": {
                            "key": {
                                "remoteJid": "556286342844",
                                "fromMe": True,
                                "id": "<string>",
                                "participant": "<string>"
                            }
                        },
                        "linkPreview": True,
                        "mentionsEveryOne": False
                }



            startChat(payload)
            
        case "Chamado solucionado":

            payload = {
                "number": f"{data['author']['mobile']}",
                "listMessage": {
                    "title": "*_CHAMADO SOLUCIONADO_*",
                    "description": f"""Olá, {data['author']['name']}!\nSeu chamado nº {data['ticket']['id']} foi solucionado!\n\t*{data['ticket']['solution']['author']}:* "{cleanHtml(data['ticket']['solution']['description'])}"\n""",
                    "buttonText": "Clique aqui para aceitar ou negar a solução",
                    "footerText": f"footer list\n{data['ticket']['url']}",
                    "sections": [
                        {
                            "title": "Aprovar solução:",
                            "rows": [
                                {
                                    "title": "Sim",
                                    "description": "A solução foi satisfatória.",
                                    "rowId": "1"
                                },
                                {
                                    "title": "Não",
                                    "description": "A solução não foi satisfatória.",
                                    "rowId": "0"
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
                                "number": f"{data['author']['mobile']}", # destinatário
                                "textMessage": {
                                    "text":f"""*_ATUALIZAÇÃO DE UM CHAMADO_*

Olá, {data['author']['name']}!
                                    
    {data['ticket']['lastupdater']} atualizou seu chamado nº {data['ticket']['id']} - {data['ticket']['title']}

Para acompanhar acesse o link: {data['ticket']['url']}
                                """
                                },
                                "delay": 1200,
                                "quoted": {
                                    "key": {
                                        "remoteJid": "556286342844",
                                        "fromMe": True,
                                        "id": "<string>",
                                        "participant": {data['author']['id']}
                                    }
                                },
                                "linkPreview": True,
                                "mentionsEveryOne": False
            }
    
            startChat(payload)
    # print(response.text)

def startChat(payload):
    url = "http://192.168.15.60:8080/message/sendText/Glpi_GBR"

    

    response = requests.request("POST", url, json=payload, headers=headers)

def sendTicketSolution(payload):
    url = "http://192.168.15.60:8080/chat/fetchProfilePictureUrl/Glpi_GBR"

    response = requests.request("POST", url, json=payload, headers=headers)

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000, debug=True)

