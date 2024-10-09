import requests

headers = {
   "Authorization": "Bearer ZvAT6r7bwE2WxA4EaZQHKtMq",
   "Content-Type": "application/json" 
}
urlSessionId = "http://192.168.15.60:3002/api/v1/typebots/teste-0fb4ec6/startChat"
preVariables = {
    "prefilledVariables": {
        "remoteJid": "556286342844@s.whatsapp.net",
        "messageType":"conversation",
        "pushName":"Cleitinho",
        "instanceName":"teste-0fb4ec6"
    }
}
# url = "http://192.168.15.60:3002/api/v1/typebots/cm1i7ui19000vjuyee0fb4ec6/startChat"

response = requests.request("POST", urlSessionId, headers=headers, json=str(preVariables))
sessionId = response.json()['sessionId']
# print(sessionId)

url = f'http://192.168.15.60:3002/api/v1/sessions/{sessionId}/continueChat'

payload = {
    "message": "Mensagem"
    # {
    #     "type": "text",
    #     "text": f"Oi",
    #     "attachedFileUrls": ["<string>"]
    # },
    # "isStreamEnabled": True,
    # "resultId": "<string>",
    # "isOnlyRegistering": True,
    # "prefilledVariables": {
    #     "remoteJid": "556286342844@s.whatsapp.net",
    #     "messageType":"conversation",
    #     "pushName":"Cleitinho",
    #     "instanceName":"teste-0fb4ec6"
    # },
    # "textBubbleContentFormat": "richText"
}
headers = {"Content-Type": "application/json"}
               
response = requests.request("POST", url, json=str(payload), headers=headers)

print(response.text)