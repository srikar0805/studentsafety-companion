
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api():
    print("Waiting for server...")
    time.sleep(10) # Wait for startup (graph loading takes time)
    
    # 1. Health
    try:
        resp = requests.get(f"{BASE_URL}/health")
        print("Health Check:", resp.json())
    except Exception as e:
        print("Server not ready:", e)
        return

    # 2. Navigate (Student Center -> Library)
    payload = {
        "origin": [38.9424, -92.3271],
        "dest": [38.9447, -92.3268],
        "mode": "safe"
    }
    resp = requests.post(f"{BASE_URL}/navigate", json=payload)
    if resp.status_code == 200:
        data = resp.json()
        print(f"Navigation Success: Distance={data['distance']}m, Risk={data['risk_score']}")
    else:
        print("Navigation Failed:", resp.text)

    # 3. Chat
    payload = {"query": "How do I report a crime?"}
    resp = requests.post(f"{BASE_URL}/chat", json=payload)
    if resp.status_code == 200:
        data = resp.json()
        print(f"Chat Answer: {data['answer'][:100]}...")
    else:
        print("Chat Failed:", resp.text)

if __name__ == "__main__":
    test_api()
