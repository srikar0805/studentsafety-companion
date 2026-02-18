"""Test Archia API connection directly."""
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ARCHIA_URL = "https://api.archia.app/v1/responses"
API_KEY = os.getenv("ARCHIA_API_KEY")
AGENT_NAME = os.getenv("ARCHIA_AGENT_NAME", "Campus Dispatch Orchestrator")

print(f"Testing Archia API")
print(f"URL: {ARCHIA_URL}")
print(f"Agent Name: '{AGENT_NAME}'")
print(f"API Key: {API_KEY[:20]}..." if API_KEY else "No API Key")
print()

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "agent": AGENT_NAME,
    "input": "Hello"
}

print("Payload being sent:")
print(payload)
print()

try:
    response = requests.post(ARCHIA_URL, json=payload, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    response.raise_for_status()
    print("\n✅ Success!")
except requests.exceptions.HTTPError as e:
    print(f"\n❌ HTTP Error: {e}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"\n❌ Error: {e}")
