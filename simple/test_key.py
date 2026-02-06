import requests

url = "http://127.0.0.1:5006/api_external/climates"
# Remplace 'TA_CLE_API_REELLE' par une clé présente dans ta table api_clients
headers = {
    "X-API-KEY": "38e3698be9aec9d481b0154b8acefd08"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("Succès !")
    print(response.json())
else:
    print(f"Erreur {response.status_code}")
    print(response.json())