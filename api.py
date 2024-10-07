from flask import Flask, request, jsonify, Response, make_response
import requests

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_post():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Invalid JSON or no JSON received"}), 400

    print(f"Received data: {data}")

    try:
        if data['ticket']['lastupdater'] != data['author']['name']:
            formatMessage(data)
    except KeyError as e:
        return jsonify({"error": f"Missing key: {e}"}), 400

    return jsonify({"received_data": data}), 200



def formatMessage(data):
    payload = {
        "number": f"{data['author']['mobile']}", # destinatário
        "textMessage": {
            "text":f"""Olá, {data['author']['name']}!
            
        {data['ticket']['action']} em seu chamado nº {data['ticket']['id']} - {data['ticket']['title']}:

        *{data['ticket']['solution']['approval']['author']}:* {data['ticket']['solution']['approval']['description']}

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

