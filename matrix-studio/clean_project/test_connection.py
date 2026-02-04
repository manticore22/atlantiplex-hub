"""
Simple test to start Atlantiplex Studio and verify it's working
"""
import subprocess
import time
import requests
import sys
import os

def test_server():
    print("=" * 60)
    print("ATLANTIPLEX STUDIO - CONNECTION TEST")
    print("=" * 60)
    
    # Change to correct directory
    os.chdir(r"C:\Users\User\Desktop\verily-project\04-FINISHED-PRODUCTS\finished products ready for launch\atlantiplex hub\matrix-studio\clean_project")
    
    # Start server in background
    print("Starting Atlantiplex Studio...")
    server_process = subprocess.Popen([
        sys.executable, 'atlantiplex_studio_refined.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Wait for startup
    print("Waiting for server to start...")
    for i in range(15):
        try:
            # Test common ports
            ports = [8080, 8086, 49872, 63859, 61551, 5000, 3000, 8000, 9000]
            for port in ports:
                try:
                    response = requests.get(f"http://127.0.0.1:{port}/api/health", timeout=1)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"\n✓ SERVER FOUND on port {port}")
                        print(f"  Status: {data['status']}")
                        print(f"  Version: {data['version']}")
                        print(f"  Features: {len(data['features'])} loaded")
                        print(f"\n🌐 Access URL: http://127.0.0.1:{port}")
                        print(f"🔑 Credentials: manticore / patriot8812")
                        print("\nServer is running and ready!")
                        return port
                except:
                    continue
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
            server_process.terminate()
            return None
        except Exception as e:
            print(f"Test error: {e}")
        
        time.sleep(1)
    
    print("\n✗ Server not found on any port after 15 seconds")
    
    # Check if server is running
    if server_process.poll() is None:
        print("Server process is running but not accessible")
    else:
        stdout, stderr = server_process.communicate()
        print("Server process has stopped")
        if stderr:
            print(f"Error: {stderr}")
        if stdout:
            print(f"Output: {stdout}")
    
    return None

if __name__ == "__main__":
    port = test_server()
    
    if port:
        print(f"\n🎉 SUCCESS! Atlantiplex Studio is running on port {port}")
        print("Keep this window open to maintain the server.")
        print("Access the web interface in your browser.")
        input("\nPress Enter to stop the server...")
    else:
        print("\n❌ FAILED: Could not start server successfully")
        print("Please check the error messages above.")
        input("Press Enter to exit...")