"""Test alternative Archia API formats."""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

ARCHIA_URL = "https://api.archia.app/v1/responses"
API_KEY = os.getenv("ARCHIA_API_KEY")
AGENT_NAME = "Campus Dispatch Orchestrator"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Test different payload formats
test_formats = [
    {
        "name": "Format 1: agent + input (current)",
        "payload": {
            "agent": AGENT_NAME,
            "input": "Hello"
        }
    },
    {
        "name": "Format 2: messages array",
        "payload": {
            "agent": AGENT_NAME,
            "messages": [{"role": "user", "content": "Hello"}]
        }
    },
    {
        "name": "Format 3: model + input",
        "payload": {
            "model": f"agent:{AGENT_NAME}",
            "input": "Hello"
        }
    },
    {
        "name": "Format 4: model + messages",
        "payload": {
            "model": AGENT_NAME,
            "messages": [{"role": "user", "content": "Hello"}]
        }
    },
    {
        "name": "Format 5: prompt field",
        "payload": {
            "agent": AGENT_NAME,
            "prompt": "Hello"
        }
    },
]

print("Testing different API payload formats...\n")

for test in test_formats:
    print(f"{'='*60}")
    print(f"Testing: {test['name']}")
    print(f"Payload: {test['payload']}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(ARCHIA_URL, json=test['payload'], headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body: {response.text[:200]}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! This format works!")
            break
    except Exception as e:
        print(f"Error: {e}")
    
    print()
