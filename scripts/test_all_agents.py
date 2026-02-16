"""Test all Archia agents to verify they're working."""
import requests
import os
from dotenv import load_dotenv
import json
import time

load_dotenv()

BASE_URL = "https://registry.archia.app"
API_KEY = os.getenv("ARCHIA_API_KEY")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# All agents from the Archia console
agents = [
    {
        "name": "Campus Dispatch Orchestrator",
        "test_input": "I need to get to Ellis Library safely"
    },
    {
        "name": "Campus Routing Engine",
        "test_input": "Find routes from Student Center to Ellis Library"
    },
    {
        "name": "Campus risk and prediction engine",
        "test_input": "Analyze safety for a route to the library"
    },
    {
        "name": "campus context and journalism agent",
        "test_input": "What are campus safety policies?"
    }
]

print("="*70)
print("TESTING ALL ARCHIA AGENTS")
print("="*70)
print()

results = []

for i, agent in enumerate(agents, 1):
    agent_name = agent["name"]
    test_input = agent["test_input"]
    
    print(f"Test {i}/{len(agents)}: {agent_name}")
    print("-"*70)
    print(f"Input: {test_input}")
    
    payload = {
        "model": f"agent:{agent_name}",
        "input": test_input,
        "stream": False
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/v1/responses",
            json=payload,
            headers=headers,
            timeout=45
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            status = result.get("status")
            
            # Extract response text
            response_text = None
            for item in result.get("output", []):
                if item.get("type") == "message":
                    for content in item.get("content", []):
                        if content.get("type") == "output_text":
                            response_text = content.get("text", "")
                            break
                    if response_text:
                        break
            
            print(f"✅ SUCCESS (status: {status}, {elapsed_time:.1f}s)")
            if response_text:
                preview = response_text[:150].replace('\n', ' ')
                print(f"Response: {preview}...")
            else:
                print(f"Response structure: {list(result.keys())}")
            
            results.append({
                "agent": agent_name,
                "status": "✅ WORKING",
                "time": f"{elapsed_time:.1f}s"
            })
        else:
            print(f"❌ FAILED - HTTP {response.status_code}")
            print(f"Error: {response.text[:200]}")
            results.append({
                "agent": agent_name,
                "status": f"❌ FAILED ({response.status_code})",
                "time": f"{elapsed_time:.1f}s"
            })
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT (>45s)")
        results.append({
            "agent": agent_name,
            "status": "❌ TIMEOUT",
            "time": ">45s"
        })
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results.append({
            "agent": agent_name,
            "status": f"❌ ERROR",
            "time": "N/A"
        })
    
    print()

# Summary
print("="*70)
print("SUMMARY")
print("="*70)
for result in results:
    print(f"{result['status']:20} {result['time']:8} - {result['agent']}")

print()
working_count = sum(1 for r in results if "✅" in r["status"])
print(f"Result: {working_count}/{len(agents)} agents working")

if working_count == len(agents):
    print("\n🎉 All agents are operational!")
elif working_count > 0:
    print(f"\n⚠️  {len(agents) - working_count} agent(s) need attention")
else:
    print("\n❌ No agents are responding - check configuration")
