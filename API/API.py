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
        name = data['author']['name']
        number = data['author']['mobile']
        # print(name)
        # print(mobile)
        startChat(name, number)
    except KeyError as e:
        return jsonify({"error": f"Missing key: {e}"}), 400

    return jsonify({"received_data": data}), 200



def startChat(name, mobile):

    sessionId = getSessionId()
    if sessionId == 0:
        print(f'deu ruim')
        return

    url = "http://192.168.15.60:3002/api/v1/typebots/brg-glpi/startChat"

    payload = {
        "number": "556286342844", # destinatário
        "textMessage": {
        "text":"fala meu bom"
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
        "mentionsEveryOne": True
    }

    headers = {
        "apikey": "07bknevdrycmun144k9plmh",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000, debug=True)

