
import requests
import json

url = "http://localhost:8000/api/routes"
payload = {
    "origin": "Student Center",
    "destination": "Jesse Hall",
    "priority": "safety",
    "user_mode": "student",
    "time": "now"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Incidents count:", len(data.get("incidents", [])))
        print("Emergency phones count:", len(data.get("emergency_phones", [])))
        print("Routes count:", len(data.get("recommendation", {}).get("routes", [])))
    else:
        print("Error:", response.text)
except Exception as e:
    print(f"Request failed: {e}")
