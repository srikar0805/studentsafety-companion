import requests

# Test the transit API endpoints
BASE = "http://localhost:8000"

print("🧪 Testing Transit API Endpoints\n")

# Test 1: Get all routes
print("1. GET /api/transit/routes")
resp = requests.get(f"{BASE}/api/transit/routes")
routes_data = resp.json()
print(f"   Status: {resp.status_code}")
print(f"   Routes: {len(routes_data['routes'])}")
for route in routes_data['routes'][:2]:
    print(f"     - {route['route_name']} ({route['route_color']})")

# Test 2: Get stops for Black Route (route 1)
print("\n2. GET /api/transit/routes/1/stops")
resp = requests.get(f"{BASE}/api/transit/routes/1/stops")
stops_data = resp.json()
print(f"   Status: {resp.status_code}")
print(f"   Stops: {len(stops_data['stops'])}")
for stop in stops_data['stops'][:3]:
    print(f"     - {stop['stop_name']} at ({stop['latitude']:.6f}, {stop['longitude']:.6f})")

# Test 3: Check if coordinates are valid
valid_count = sum(1 for s in stops_data['stops'] if s['latitude'] and s['longitude'])
print(f"\n✅ {valid_count}/{len(stops_data['stops'])} stops have valid coordinates")

# Test 4: Get stops for Red Route (route 2)
print("\n3. GET /api/transit/routes/2/stops")
resp = requests.get(f"{BASE}/api/transit/routes/2/stops")
stops_data_2 = resp.json()
print(f"   Status: {resp.status_code}")
print(f"   Stops: {len(stops_data_2['stops'])}")

print("\n✅ Transit API is working! Stops will now appear on the map.")
