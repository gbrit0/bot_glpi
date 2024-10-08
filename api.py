from flask import Flask, request, jsonify, Response, make_response
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_post():
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




        case "Chamado solucionado":
           payload = {
                        "number": f"{data['author']['mobile']}", # destinatário
                        "textMessage": {
                            "text":f"""*_CHAMADO SOLUCIONADO_*

Olá, {data['author']['name']}!
                            
Seu chamado nº {data['ticket']['id']} foi solucionado!

    *{data['ticket']['solution']['author']}:* "{cleanHtml(data['ticket']['solution']['description'])}"

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
                                        "participant": "<string>"
                                    }
                                },
                                "linkPreview": True,
                                "mentionsEveryOne": False
            }
    
    startChat(payload)
    # print(response.text)

def startChat(payload):
    url = "http://192.168.15.60:8080/message/sendText/Glpi_GBR"

    headers = {
        "apikey": "07bknevdrycmun144k9plmh",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000, debug=True)

