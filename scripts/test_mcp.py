"""Test MCP endpoints."""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test MCP health endpoint."""
    print("Testing /mcp/health...")
    response = requests.get(f"{BASE_URL}/mcp/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_route():
    """Test route tool endpoint."""
    print("Testing /mcp/route...")
    payload = {
        "origin": {"latitude": 38.9446, "longitude": -92.3246},
        "destination": {"latitude": 38.9519, "longitude": -92.3281},
        "risk_weight": 0.7,
        "time_weight": 0.3
    }
    response = requests.post(f"{BASE_URL}/mcp/route", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Routes returned: {len(data.get('routes', []))}")
        if data.get('routes'):
            print(f"First route distance: {data['routes'][0]['distance_meters']}m")
            print(f"First route ETA: {data['routes'][0]['eta_minutes']:.1f} min")
    else:
        print(f"Error: {response.text}")
    print()

def test_rag():
    """Test RAG tool endpoint."""
    print("Testing /mcp/rag...")
    payload = {
        "query": "campus safety policies",
        "top_k": 3
    }
    response = requests.post(f"{BASE_URL}/mcp/rag", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Results returned: {data.get('count', 0)}")
    print()

def test_traffic():
    """Test traffic tool endpoint."""
    print("Testing /mcp/traffic...")
    payload = {
        "geometry": {
            "type": "LineString",
            "coordinates": [[-92.3246, 38.9446], [-92.3281, 38.9519]]
        },
        "radius_m": 500,
        "days_back": 90
    }
    response = requests.post(f"{BASE_URL}/mcp/traffic", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Stop count: {data.get('stop_count')}")
        print(f"Patrol frequency: {data.get('patrol_frequency')}")
    else:
        print(f"Error: {response.text}")
    print()

if __name__ == "__main__":
    try:
        test_health()
        test_route()
        test_rag()
        test_traffic()
        print("✓ All MCP endpoints are accessible!")
    except Exception as e:
        print(f"✗ Error: {e}")
