#!/usr/bin/env python3
"""
Matrix Unified Broadcasting Studio - Simple Launcher
Fixed version without Unicode characters for Windows compatibility
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8+ is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"Python {sys.version.split()[0]} detected")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask', 'flask_socketio', 'flask_cors', 'flask_sqlalchemy',
        'flask_jwt_extended', 'cv2', 'psutil', 'websockets', 'apscheduler'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print("Installing missing dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing)
        print("Dependencies installed!")
    else:
        print("All dependencies are installed!")
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'logs', 'core/uploads', 'core/logs']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print("Directories created!")

def launch_server():
    """Launch the production backend"""
    print("Starting Matrix Unified Broadcasting Studio...")
    print("=" * 60)
    print("Web Interface: http://localhost:8080")
    print("API Documentation: http://localhost:8080/api")
    print("Demo Login: username: demo, password: demo123")
    print("=" * 60)
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        subprocess.run([sys.executable, 'production_ready_backend.py'])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

def main():
    """Main launcher function"""
    print("MATRIX UNIFIED BROADCASTING STUDIO")
    print("SIMPLE LAUNCHER")
    print("=" * 60)
    print()
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return
    
    # Check and install dependencies
    if not check_dependencies():
        input("Press Enter to exit...")
        return
    
    # Create directories
    create_directories()
    
    # Launch server
    launch_server()

if __name__ == '__main__':
    main()