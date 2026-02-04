#!/usr/bin/env python3
"""
ATLANTIPLEX MATRIX STUDIO - MINIMAL TEST VERSION
"""

from flask import Flask
import socket

# Create Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "ATLANTIPLEX MATRIX STUDIO - SERVER IS WORKING!"

@app.route('/test')
def test():
    return "ROUTE TEST - SUCCESS!"

if __name__ == '__main__':
    # Test port availability
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8080))
    sock.close()
    
    if result == 0:
        print("ERROR: Port 8080 is already in use!")
        print("Please stop the existing server first.")
        exit(1)
    else:
        print("Port 8080 is available - starting server...")
        
    print("=" * 50)
    print("ATLANTIPLEX MATRIX STUDIO")
    print("Starting minimal test server")
    print("=" * 50)
    
    try:
        app.run(host='127.0.0.1', port=8080, debug=False)
    except Exception as e:
        print(f"Server error: {e}")
        exit(1)