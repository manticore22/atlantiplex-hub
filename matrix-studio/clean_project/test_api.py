"""
Quick test for Atlantiplex Studio API endpoints
"""
import requests
import json
import time

def test_api():
    # Find a test port
    base_url = "http://127.0.0.1:49873"
    
    print("Testing Atlantiplex Studio API...")
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✓ Health endpoint working:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"✗ Health endpoint failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Server not running. Please start Atlantiplex Studio first.")
        return
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    # Test database
    try:
        response = requests.get(f"{base_url}/test/database")
        print(f"\n✓ Database test: {response.json()}")
    except Exception as e:
        print(f"✗ Database test failed: {e}")
    
    # Test Azure (will likely show not available)
    try:
        response = requests.get(f"{base_url}/test/azure")
        print(f"✓ Azure test: {response.json()}")
    except Exception as e:
        print(f"✗ Azure test failed: {e}")
    
    print("\nAPI Test Complete!")

if __name__ == "__main__":
    test_api()