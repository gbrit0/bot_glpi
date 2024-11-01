import requests
import base64

baseUrl = 'localhost/apirest.php'

app_token = "<app_token>"
auth = "user_token <user_token>"

def initSession():
   headers = {
        "Authorization": f"{auth}",
        "App-Token": f"{app_token}",
        "Content-Type": "application/json"
    }

   url = f"{baseUrl}/initSession/"

   response = requests.request("GET", url, headers=headers)
   return response.json()['session_token']

def killSession(session_token):
   headers = {
      "Session-Token": f"{session_token}",
      "App-Token": f"{app_token}",
      "Content-Type": "application/json"
   }

   url = f"{baseUrl}/killSession"

   response = requests.request("GET", url, headers=headers)
   
def getMyProfiles(session_token):
   headers = {
      "Session-Token": f"{session_token}",
      "App-Token": f"{app_token}",
      "Content-Type": "application/json"
   }

   url = f"{baseUrl}/getMyProfiles"

   response = requests.request("GET", url, headers=headers)
   print(response.json())

def getMyEntities(session_token):
   headers = {
      "Session-Token": f"{session_token}",
      "App-Token": f"{app_token}",
      "Content-Type": "application/json"
   }

   url = f"{baseUrl}/getMyEntities"

   response = requests.request("GET", url, headers=headers)
   print(response.json())

def searchOptions(session_token):
   headers = {
      "Session-Token": f"{session_token}",
      "App-Token": f"{app_token}",
      "Content-Type": "application/json"
   }

   url = f"{baseUrl}/listSearchOptions/Ticket"

   response = requests.request("GET", url, headers=headers)
   print(response.json())

def searchItems(session_token):
   headers = {
      "Session-Token": f"{session_token}",
      "App-Token": f"{app_token}",
      "Content-Type": "application/json"
   }

   url = f"{baseUrl}/search/AllAssets"

   response = requests.request("GET", url, headers=headers)
   print(response.json())

def getMassiveActions(session_token):
   headers = {
      "Session-Token": f"{session_token}",
      "App-Token": f"{app_token}",
      "Content-Type": "application/json"
   }

   url = f"{baseUrl}/getMassiveActions/Ticket/"

   response = requests.request("GET", url, headers=headers)
   print(response.json())

# curl -X PUT \
# -H 'Content-Type: application/json' \
# -H "Session-Token: YOUR_SESSION_TOKEN" \
# -H "App-Token: YOUR_APP_TOKEN" \
# -d '{"input": {"id": TICKET_ID, "status": 6, "solution": "Aprovado"}}' \
# 'http://path/to/glpi/apirest.php/Ticket/TICKET_ID'

def updateItem(session_token, ticket_id):
   headers = {
      "Session-Token": f"{session_token}",
      "App-Token": f"{app_token}",
      "Content-Type": "application/json"
   }

   url = f"{baseUrl}/Ticket/{ticket_id}"

   payload = {
      "input":{
         "id":f"{ticket_id}",
         "status":6,
         "solution":"Aprovado"
      }
   }

   response = requests.request("PUT", url, headers=headers, json=payload)
   print(response.json())

def main():
   session_token = initSession()

   searchItems(session_token)

   killSession(session_token)



if __name__ == "__main__":
   main()
