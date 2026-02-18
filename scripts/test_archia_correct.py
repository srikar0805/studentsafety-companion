"""Test Archia connection with correct endpoint and format."""
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

BASE_URL = "https://registry.archia.app"
API_KEY = os.getenv("ARCHIA_API_KEY")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print("="*60)
print("ARCHIA CLOUD CONNECTION TEST")
print("="*60)
print(f"Base URL: {BASE_URL}")
print(f"API Key: {API_KEY[:20]}...")
print()

# Step 1: List available agents
print("Step 1: Listing available agents...")
print("-"*60)
try:
    response = requests.get(f"{BASE_URL}/v1/agent", headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        agents = response.json()
        print("✅ Successfully retrieved agents!")
        print(f"Response: {json.dumps(agents, indent=2)}")
        
        # Extract agent names
        if isinstance(agents, dict) and "agents" in agents:
            agent_list = agents["agents"]
            print(f"\nFound {len(agent_list)} agents:")
            for agent in agent_list:
                name = agent.get("name") or agent.get("id") or agent.get("system_name")
                print(f"  - {name}")
        else:
            print("Unexpected response format")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("="*60)

# Step 2: Test model listing
print("Step 2: Listing available models...")
print("-"*60)
try:
    response = requests.get(f"{BASE_URL}/v1/models", headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        models = response.json()
        print("✅ Successfully retrieved models!")
        if isinstance(models, dict) and "models" in models:
            print(f"Found {len(models['models'])} models")
            # Print first 5 model names
            for model in models["models"][:5]:
                name = model.get("system_name") or model.get("name") or model.get("id")
                print(f"  - {name}")
            if len(models['models']) > 5:
                print(f"  ... and {len(models['models']) - 5} more")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("="*60)

# Step 3: Test agent call with correct format
print("Step 3: Testing agent call...")
print("-"*60)

# Try different agent name formats
agent_names_to_try = [
    "campus_dispatch_orchestrator",
    "Campus Dispatch Orchestrator",
    "campusdispatchorchestrator",
]

for agent_name in agent_names_to_try:
    print(f"\nTrying agent name: '{agent_name}'")
    
    payload = {
        "model": f"agent:{agent_name}",
        "input": "Hello",
        "stream": False
    }
    
    print(f"Payload: {payload}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/responses",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)[:500]}")
            break
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {e}")

print()
print("="*60)
print("Test complete!")
