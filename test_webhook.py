import requests

user_message = "Can you tell me about black holes in 3-4 lines"
request_message = {"message": user_message}
url = "http://localhost:5678/webhook/1cb8c062-ad8a-4fbf-8299-b4c9550b20a8"

response = requests.post(url, json=request_message)

print(response.status_code)
print(response.json()[0]["output"])