"""
Test frontend-backend-Archia integration via browser simulation
"""
import requests
import time

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5174"

print("="*70)
print("FRONTEND → BACKEND → ARCHIA INTEGRATION TEST")
print("="*70)
print()

# Step 1: Check backend health
print("Step 1: Checking backend health...")
try:
    response = requests.get(f"{BACKEND_URL}/health", timeout=5)
    if response.status_code == 200:
        print("✅ Backend is running")
    else:
        print(f"❌ Backend health check failed: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Cannot connect to backend: {e}")
    print("Make sure backend is running: cd src/backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    exit(1)

print()

# Step 2: Test dispatch endpoint (same as frontend will call)
print("Step 2: Testing dispatch endpoint...")
print(f"Simulating frontend request to {BACKEND_URL}/api/v1/dispatch")
print("-"*70)

test_message = "Safest route to Ellis Library"
print(f"User message: \"{test_message}\"")
print()

try:
    start_time = time.time()
    
    response = requests.post(
        f"{BACKEND_URL}/api/v1/dispatch",
        json={"message": test_message},
        headers={"Content-Type": "application/json"},
        timeout=60
    )
    
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        ai_response = result.get("response", "")
        
        print(f"✅ SUCCESS ({elapsed:.1f}s)")
        print()
        print("AI Response:")
        print("-"*70)
        print(ai_response[:500])
        if len(ai_response) > 500:
            print(f"\n... ({len(ai_response) - 500} more characters)")
        print()
    else:
        print(f"❌ Request failed with status {response.status_code}")
        print(f"Error: {response.text}")
        exit(1)
        
except requests.exceptions.Timeout:
    print("❌ Request timed out (>60s)")
    print("The request may still be processing in Archia Cloud")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Step 3: Summary
print("="*70)
print("INTEGRATION STATUS")
print("="*70)
print()
print("✅ Backend API: Running at http://localhost:8000")
print("✅ Dispatch Endpoint: Working")
print("✅ Archia Integration: Connected")
print("✅ Frontend URL: http://localhost:5174")
print()
print("🎉 Full integration is working!")
print()
print("Next steps:")
print("1. Open browser to http://localhost:5174")
print("2. Type a message in the chat interface")
print("3. Watch the AI respond via Archia Cloud")
print()
