#!/usr/bin/env python3
"""
🌊 MATRIX UNIFIED BROADCASTING STUDIO - ONE-CLICK SETUP & LAUNCH
Complete setup with full functionality preservation and immediate launch
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
        print(f"   Current version: {sys.version}")
        return False
    print(f"Python {sys.version.split()[0]} detected")
    return True

def create_virtual_env():
    """Create virtual environment if it doesn't exist"""
    if not os.path.exists('venv'):
        print("Creating virtual environment...")
        result = subprocess.run([sys.executable, '-m', 'venv', 'venv'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to create venv: {result.stderr}")
            return False
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment exists")
    return True

def activate_venv_and_install():
    """Activate virtual environment and install dependencies"""
    print("📦 Installing dependencies...")
    
    # Determine activation script based on OS
    if os.name == 'nt':  # Windows
        pip_path = 'venv\\Scripts\\pip'
        python_path = 'venv\\Scripts\\python'
    else:  # Linux/Mac
        pip_path = 'venv/bin/pip'
        python_path = 'venv/bin/python'
    
    # Upgrade pip first
    print("   📈 Upgrading pip...")
    result = subprocess.run([pip_path, 'install', '--upgrade', 'pip'], 
                          capture_output=True, text=True)
    
    # Install core dependencies
    packages = [
        'flask>=2.3.0',
        'flask-socketio>=5.3.0',
        'flask-cors>=4.0.0',
        'flask-jwt-extended>=4.5.0',
        'flask-sqlalchemy>=3.0.0',
        'requests>=2.31.0',
        'pillow>=10.0.0',
        'opencv-python>=4.8.0',
        'websockets>=12.0',
        'psutil>=5.9.0',
        'python-dotenv>=1.0.0',
        'obs-websocket-py>=1.0.0',
        'aiortc>=1.6.0'
    ]
    
    for package in packages:
        print(f"   📦 Installing {package}...")
        result = subprocess.run([pip_path, 'install', package], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"   ⚠️  Warning: Failed to install {package}")
    
    print("✅ Dependencies installation completed")
    return python_path

def create_minimal_structure():
    """Create minimal necessary structure"""
    print("📁 Creating project structure...")
    
    directories = ['core/logs', 'core/uploads', 'web/templates', 'web/static']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Project structure created")

def create_basic_config():
    """Create basic configuration files"""
    print("⚙️ Creating configuration...")
    
    # Create basic .env file if it doesn't exist
    if not os.path.exists('web/.env'):
        env_content = f"""# Matrix Unified Broadcasting Studio Configuration
SECRET_KEY=matrix-studio-secret-key-{int(time.time())}
SQLALCHEMY_DATABASE_URI=sqlite:///matrix_unified.db
JWT_SECRET_KEY=matrix-jwt-secret-{int(time.time())}
HOST=0.0.0.0
PORT=8080
DEBUG=false
MAX_GUESTS=8
DEFAULT_QUALITY=720p
LOG_LEVEL=INFO
OBS_ENABLED=true
OBS_HOST=localhost
OBS_PORT=4444
OBS_PASSWORD=
WEBRTC_STUN_SERVER=stun:stun.l.google.com:19302
CORS_ENABLED=true
ALLOWED_ORIGINS=http://localhost:8080
"""
        with open('web/.env', 'w') as f:
            f.write(env_content)
        print("✅ Configuration file created")

def create_minimal_launcher():
    """Create minimal launcher script"""
    launcher_content = '''@echo off
REM 🌊 MATRIX UNIFIED BROADCASTING STUDIO - MINIMAL LAUNCHER
title Matrix Unified Broadcasting Studio
cd /d "%~dp0"

echo 🌊 Matrix Unified Broadcasting Studio
echo ========================================
echo.

if not exist "venv" (
    echo 🐍 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

call venv\\Scripts\\activate.bat

echo 🚀 Starting Matrix Unified Broadcasting Studio...
echo 📍 Studio Interface: http://localhost:8080
echo 👥 Guest Interface: http://localhost:8080/guest-view/[guest-id]
echo 📊 Health Check: http://localhost:8080/api/health
echo.
echo 💡 Press Ctrl+C to stop the server
echo ========================================
echo.

REM Try to find and run the main server
if exist "core\\unified_broadcast_server.py" (
    cd core
    python unified_broadcast_server.py %*
) else if exist "unified_broadcast_server.py" (
    python unified_broadcast_server.py %*
) else if exist "matrix_broadcast_studio_complete.py" (
    python matrix_broadcast_studio_complete.py %*
) else if exist "app.py" (
    python app.py %*
) else (
    echo ❌ No main server file found
    echo 💡 Please ensure you have a server file in the current directory
    pause
)
'''
    
    with open('QUICK_START.bat', 'w') as f:
        f.write(launcher_content)
    print("✅ Quick launcher created")

def launch_server(python_path):
    """Launch the server"""
    print("🚀 Starting Matrix Unified Broadcasting Studio...")
    print("=" * 60)
    print("📍 Studio Interface: http://localhost:8080")
    print("👥 Guest Interface: http://localhost:8080/guest-view/[guest-id]")
    print("📊 Health Check: http://localhost:8080/api/health")
    print("=" * 60)
    print()
    
    # Try to find the main server file
    server_files = [
        'core/unified_broadcast_server.py',
        'unified_broadcast_server.py', 
        'matrix_broadcast_studio_complete.py',
        'app.py'
    ]
    
    server_file = None
    for file_path in server_files:
        if os.path.exists(file_path):
            server_file = file_path
            break
    
    if server_file:
        try:
            # Launch the server
            if os.name == 'nt':  # Windows
                subprocess.run([python_path, server_file] + sys.argv[1:])
            else:  # Linux/Mac
                os.execv(python_path, [python_path, server_file] + sys.argv[1:])
        except KeyboardInterrupt:
            print("\n✅ Server stopped by user")
        except Exception as e:
            print(f"❌ Error starting server: {e}")
    else:
        print("❌ No server file found")
        print("💡 Available files in directory:")
        for file in os.listdir('.'):
            if file.endswith('.py'):
                print(f"   - {file}")

def main():
    """Main setup and launch function"""
    print("MATRIX UNIFIED BROADCASTING STUDIO")
    print("ONE-CLICK SETUP & LAUNCH")
    print("=" * 60)
    print()
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return
    
    # Create virtual environment
    if not create_virtual_env():
        input("Press Enter to exit...")
        return
    
    # Activate venv and install dependencies
    python_path = activate_venv_and_install()
    if not python_path:
        input("Press Enter to exit...")
        return
    
    # Create minimal structure
    create_minimal_structure()
    
    # Create configuration
    create_basic_config()
    
    # Create launcher
    create_minimal_launcher()
    
    print()
    print("🎉 SETUP COMPLETED!")
    print("=" * 60)
    print()
    
    # Launch server
    launch_server(python_path)

if __name__ == '__main__':
    main()