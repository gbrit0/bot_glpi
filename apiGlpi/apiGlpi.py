import requests
import base64

baseUrl = 'http://192.168.15.60/apirest.php'

user_token = "L6an8rJwuy1bYjHwx72a6ytdLwz80B7aSWoNc1yW"
app_token = "iXrMsWsxvJoF2ikQsPLFa8W8yFv9JZQnWxnBkjBG"
auth = "user_token L6an8rJwuy1bYjHwx72a6ytdLwz80B7aSWoNc1yW"



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


def main():
   session_token = initSession()

   getMyProfiles(session_token)

   killSession(session_token)



if __name__ == "__main__":
   main()
