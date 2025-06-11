import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)
url = f"{os.getenv('EVOLUTION_API_BASE_URL')}/message/sendText/testes_bot"

payload = {
   "number": f"556237712556",
   "text":f"""Teste de envio direto""",
   "delay": 2000
}

response = requests.request(
   "POST", 
   url, 
   json=payload, 
   headers={
      "apikey": f"8D0CE98BBBF1-48EB-BD48-380B398EA42D",
      "Content-Type": "application/json"
   }
)

data = response.json()
print(data)