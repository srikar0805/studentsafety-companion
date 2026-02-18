"""
Test Archia integration through backend dispatch endpoint.
This mimics what the frontend will send.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_dispatch_endpoint():
    """Test the /api/v1/dispatch endpoint that calls Archia."""
    print("=" * 60)
    print("Testing Backend → Archia Integration")
    print("=" * 60)
    print()
    
    test_messages = [
        "Hello",
        "Safest route to Ellis Library",
        "I need to walk to the rec center at 10pm",
    ]
    
    for idx, message in enumerate(test_messages, 1):
        print(f"Test {idx}: {message}")
        print("-" * 60)
        
        payload = {"message": message}
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/dispatch",
                json=payload,
                timeout=35
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS!")
                print(f"Response: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out (>35s)")
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to backend (is it running on port 8000?)")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
    
    print("=" * 60)

def test_mcp_endpoints():
    """Quick test that MCP endpoints are accessible."""
    print("Testing MCP Tool Endpoints")
    print("-" * 60)
    
    # Test health
    try:
        response = requests.get(f"{BASE_URL}/mcp/health")
        if response.status_code == 200:
            print("✅ /mcp/health is running")
        else:
            print(f"⚠️ /mcp/health returned {response.status_code}")
    except:
        print("❌ /mcp/health is not accessible")
    
    print()

if __name__ == "__main__":
    print("\n")
    test_mcp_endpoints()
    test_dispatch_endpoint()
    print("Test complete!")
