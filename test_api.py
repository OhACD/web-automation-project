import requests

response = requests.post("http://127.0.0.1:8000/automate", json={"run": True})
print(response.status_code)
print(response.json())
