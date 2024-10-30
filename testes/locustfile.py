from locust import HttpUser, TaskSet, task, between

class ChatbotTasks(TaskSet):

   @task(1)
   def send_message(self):
      

      payload={
         "test":"data"
      }
      self.client.post("/webhook", json=payload)

class ChatbotUser(HttpUser):
   tasks = [ChatbotTasks]
   wait_time = between(5, 10)  # Intervalo entre as requisições (1 a 5 segundos)
