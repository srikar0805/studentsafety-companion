
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(name, endpoint, payload):
    print(f"Testing {name} ({endpoint})...")
    try:
        resp = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=30)
        if resp.status_code == 200:
            print(f"✅ {name}: Success")
            # print(json.dumps(resp.json(), indent=2)[:200] + "...")
            return True
        else:
            print(f"❌ {name}: Failed {resp.status_code}")
            print(resp.text)
            return False
    except Exception as e:
        print(f"❌ {name}: Error {e}")
        return False

def main():
    print("--- Local MCP Test ---\n")
    
    # 0. Health
    if not test_endpoint("Health", "/health", {}):
        print("CRITICAL: Health check failed. Server might be down.")
        return

    # 1. Route
    test_endpoint("Route (String)", "/mcp/route", {
        "origin": "Student Center",
        "destination": "Ellis Library",
        "priority": "safety"
    })
    
    # 2. Risk (Need a mock route)
    # We can use the result from Route if it works, or mock it.
    # Let's try to get a real route first.
    route_resp = requests.post(f"{BASE_URL}/mcp/route", json={
        "origin": "Student Center", "destination": "Ellis Library"
    })
    
    routes = []
    if route_resp.status_code == 200:
        routes = route_resp.json().get("routes", [])
        
    if routes:
        test_endpoint("Risk", "/mcp/risk", {"routes": routes})
        test_endpoint("RAG", "/mcp/rag", {"routes": routes})
        test_endpoint("Traffic", "/mcp/traffic", {"routes": routes})
    else:
        print("⚠️ Skipping Risk/RAG/Traffic tests because Route failed to return routes.")

    # 3. Shuttle
    test_endpoint("Shuttle", "/mcp/shuttle", {"location": "Student Center"})

if __name__ == "__main__":
    main()
