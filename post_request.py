import requests

url = "http://127.0.0.1:8000/automate"

payload = {
    "run": True,
    "item": "Sauce Labs Fleece Jacket", # optional, overrides default ITEM_TO_LOOKUP
    "timeout": 45                   # optional, overrides default SCRIPT_TIMEOUT
}

response = requests.post(url, json=payload)

print("Status Code: ", response.status_code)
print("JSON Response: ", response.json())