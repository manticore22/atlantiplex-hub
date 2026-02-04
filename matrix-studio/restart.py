#!/usr/bin/env python3
"""
Quick launcher to restart the app with template folder fix
"""

import subprocess
import sys
import os
import time

print("Restarting Atlantiplex Matrix Studio with template fix...")
print("Stopping any existing server...")

# Wait a moment for any existing server to stop
time.sleep(2)

print("Starting server with updated configuration...")
print("Web Interface: http://localhost:8080")
print("Press Ctrl+C to stop")
print("=" * 50)

# Start the app
try:
    subprocess.run([sys.executable, 'app.py'])
except KeyboardInterrupt:
    print("\nServer stopped by user")
except Exception as e:
    print(f"Error starting server: {e}")