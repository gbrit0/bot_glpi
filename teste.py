import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)
url = f"{os.getenv('EVOLUTION_API_BASE_URL')}/message/sendList/{os.getenv('EVOLUTION_INSTANCE')}"

payload = {
   "number": f"5562986342844",
   "ticke_id": f"12345",
   "title": "*_CHAMADO SOLUCIONADO_*",
   "description": f"""Chamado Solucionado""",
   "buttonText": "Clique aqui para aceitar ou negar a solução",
   "footerText": f"Para acompanhar acesse o link:\ngoogle.com",
   "sections": [
      {
            "title": "Aprovar solução:",
            "rows": [
               {
                  "title": "Sim",
                  "description": "A solução foi satisfatória.",
                  "rowId": f"d1" # passando o ticketId para recuperar mais fácil na hora de enviar a aprovação
               },
               {
                  "title": "Não",
                  "description": "A solução não foi satisfatória.",
                  "rowId": f"2f" # passando o ticketId para recuperar mais fácil na hora de enviar a aprovação
               }
            ]
      }
   ],
   "options": {
      "delay": 1200,
      "presence": "composing"
   },
   "quoted": {
      "key": {
         "fromMe": True,
         "type":"Chamado solucionado",
         "id":""
      }
   }
}

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
print(data)