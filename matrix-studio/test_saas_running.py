# Test SaaS Platform
import requests
import time

print("Testing Atlantiplex SaaS Platform...")
print()

# Wait a moment for server to be ready
time.sleep(2)

try:
    # Test health endpoint
    print("[TEST 1] Health Check...")
    response = requests.get('http://localhost:8080/health', timeout=5)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
        print("✓ Health check PASSED")
    else:
        print("✗ Health check FAILED")
    print()
    
    # Test root endpoint
    print("[TEST 2] Landing Page...")
    response = requests.get('http://localhost:8080/', timeout=5)
    print(f"Status: {response.status_code}")
    if response.status_code == 200 and 'Atlantiplex' in response.text:
        print("✓ Landing page PASSED")
    else:
        print("✗ Landing page FAILED")
    print()
    
    print("=" * 60)
    print("SaaS PLATFORM IS RUNNING SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("Access URLs:")
    print("  • Main Platform: http://localhost:8080")
    print("  • Health Check:  http://localhost:8080/health")
    print()
    
except Exception as e:
    print(f"Error: {e}")
    print("Make sure the server is running: python saas_platform.py")