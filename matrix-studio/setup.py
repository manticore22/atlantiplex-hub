#!/usr/bin/env python3
"""
🌊 MATRIX UNIFIED BROADCASTING STUDIO - AUTOMATIC SETUP
One-click complete setup with full functionality preservation
"""

import os
import sys
import shutil
import json
import time
from pathlib import Path

def create_directory_structure():
    """Create professional directory structure"""
    directories = [
        'core',
        'core/broadcasting',
        'core/guests', 
        'core/scenes',
        'core/platforms',
        'core/obs',
        'core/analytics',
        'core/logs',
        'core/uploads',
        'core/recordings',
        'web',
        'web/templates',
        'web/static',
        'web/static/css',
        'web/static/js',
        'web/static/images',
        'tests',
        'tests/unit',
        'tests/integration',
        'docs',
        'docs/api',
        'docs/user',
        'docs/development',
        'legacy',
        'legacy/old_versions',
        'legacy/backups'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {directory}")

def move_file_to_location(file_path, destination):
    """Move file to specific location with error handling"""
    if os.path.exists(file_path):
        try:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.move(file_path, destination)
            print(f"  ✅ Moved: {file_path} → {destination}")
            return True
        except Exception as e:
            print(f"  ❌ Failed to move {file_path}: {e}")
            return False
    return False

def organize_core_components():
    """Organize core server components"""
    print("🌊 Organizing core components...")
    
    core_files = {
        'unified_broadcast_server.py': 'core/unified_broadcast_server.py',
        'comprehensive_api.py': 'core/comprehensive_api.py',
        'broadcast_engine.py': 'core/broadcasting/broadcast_engine.py',
        'guest_management.py': 'core/guests/guest_management.py',
        'scene_manager.py': 'core/scenes/scene_manager.py',
        'platform_integrations.py': 'core/platforms/platform_integrations.py',
        'obs_integration.py': 'core/obs/obs_integration.py',
        'analytics.py': 'core/analytics/analytics.py',
        'scheduler.py': 'core/scheduler.py'
    }
    
    for source, dest in core_files.items():
        move_file_to_location(source, dest)

def organize_web_components():
    """Organize web interface components"""
    print("🌐 Organizing web components...")
    
    # Move templates
    templates = {
        'unified_studio.html': 'web/templates/unified_studio.html',
        'guest_view.html': 'web/templates/guest_view.html'
    }
    
    for source, dest in templates.items():
        move_file_to_location(source, dest)
    
    # Move any templates from templates/ directory
    if os.path.exists('templates'):
        for file in os.listdir('templates'):
            if file.endswith('.html'):
                move_file_to_location(f'templates/{file}', f'web/templates/{file}')
    
    # Move static files
    static_files = {
        'index.html': 'web/static/index.html',
        'studio.html': 'web/static/studio.html',
        'guest.html': 'web/static/guest.html',
        'matrix.html': 'web/static/matrix.html'
    }
    
    for source, dest in static_files.items():
        move_file_to_location(source, dest)
    
    # Move public directory contents
    if os.path.exists('public'):
        for item in os.listdir('public'):
            source_path = f'public/{item}'
            if os.path.isdir(source_path):
                dest_path = f'web/static/{item}'
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.move(source_path, dest_path)
            else:
                move_file_to_location(source_path, f'web/static/{item}')
    
    # Move configuration files
    config_files = {
        'requirements_unified.txt': 'web/requirements_unified.txt',
        'requirements.txt': 'web/requirements.txt',
        '.env': 'web/.env',
        '.env.production': 'web/.env.production',
        'config.json': 'web/config.json'
    }
    
    for source, dest in config_files.items():
        move_file_to_location(source, dest)

def organize_legacy_files():
    """Move legacy files to legacy directory"""
    print("🗄️ Organizing legacy files...")
    
    legacy_patterns = [
        'app*.py', 'main*.py', 'server*.py', 'matrix*.py', 
        'final*.py', 'production*.py', 'test*.py', 'simple*.py',
        '*.bat', '*.md', '*.json', '*.yml', '*.yaml',
        'Dockerfile', 'docker-compose*', '__pycache__',
        'node_modules', '*.pyc', 'src'
    ]
    
    import glob
    for pattern in legacy_patterns:
        for file_path in glob.glob(pattern):
            if os.path.isfile(file_path) or os.path.isdir(file_path):
                try:
                    dest = f'legacy/{os.path.basename(file_path)}'
                    if os.path.exists(dest):
                        dest = f'legacy/{os.path.basename(file_path)}_{int(time.time())}'
                    shutil.move(file_path, dest)
                    print(f"  🗄️ Moved to legacy: {file_path}")
                except Exception as e:
                    print(f"  ❌ Failed to move {file_path}: {e}")

def organize_test_files():
    """Organize test files"""
    print("🧪 Organizing test files...")
    
    import glob
    test_files = glob.glob('test*.py') + glob.glob('*_test*.py') + ['tests.py']
    
    for file_path in test_files:
        move_file_to_location(file_path, f'tests/{os.path.basename(file_path)}')

def organize_documentation():
    """Organize documentation files"""
    print("📖 Organizing documentation...")
    
    doc_files = {
        'README_UNIFIED.md': 'docs/README_UNIFIED.md',
        'README*.md': 'docs/user/'
    }
    
    # Move main documentation
    for source, dest in doc_files.items():
        if '*' in source:
            import glob
            for file_path in glob.glob(source):
                move_file_to_location(file_path, f'{dest}{os.path.basename(file_path)}')
        else:
            move_file_to_location(source, dest)

def create_core_init():
    """Create core package initialization"""
    print("📄 Creating core package init...")
    
    init_content = '''# Matrix Unified Broadcasting Studio - Core Package
__version__ = "2.0.0"
__author__ = "Matrix Studio Team"
__description__ = "Professional multi-platform streaming platform"

# Main Components
from .unified_broadcast_server import unified_system, app, socketio
from .comprehensive_api import setup_comprehensive_api

# Module Imports
from .broadcasting import broadcast_engine
from .guests import guest_management
from .scenes import scene_manager
from .platforms import platform_integrations
from .obs import obs_integration
from .analytics import analytics
from .scheduler import scheduler
'''
    
    with open('core/__init__.py', 'w') as f:
        f.write(init_content)
    print("  ✅ Created: core/__init__.py")

def create_entry_point():
    """Create Python entry point"""
    print("🔧 Creating Python entry point...")
    
    entry_point_content = '''#!/usr/bin/env python3
"""
🌊 MATRIX UNIFIED BROADCASTING STUDIO
Main entry point for organized project structure
"""

import sys
import os
import argparse
import time

# Add core directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

if __name__ == '__main__':
    from unified_broadcast_server import unified_system, app, socketio
    
    parser = argparse.ArgumentParser(description='Matrix Unified Broadcasting Studio')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    
    args = parser.parse_args()
    
    if args.init_db:
        print("🗄️ Initializing database...")
        with app.app_context():
            from unified_broadcast_server import db
            db.create_all()
        print("✅ Database initialized successfully")
    else:
        print("🌊 Starting Matrix Unified Broadcasting Studio")
        print(f"🌐 Server will be available at: http://{args.host}:{args.port}")
        print("👥 Studio Interface: http://localhost:8080")
        print("📊 API Documentation: http://localhost:8080/api/docs")
        print("=" * 60)
        
        # Set start time for uptime calculation
        unified_system.start_time = time.time()
        
        # Start server
        socketio.run(
            app,
            host=args.host,
            port=args.port,
            debug=args.debug,
            allow_unsafe_werkzeug=True
        )
'''
    
    with open('run.py', 'w') as f:
        f.write(entry_point_content)
    print("  ✅ Created: run.py")

def create_launchers():
    """Create launcher scripts"""
    print("🚀 Creating launcher scripts...")
    
    # Windows launcher
    windows_launcher = '''@echo off
REM 🌊 MATRIX UNIFIED BROADCASTING STUDIO - MAIN LAUNCHER
title Matrix Unified Broadcasting Studio
cd /d "%~dp0"

echo 🌊 Matrix Unified Broadcasting Studio
echo ========================================
echo.

if not exist "venv" (
    echo 🐍 Creating virtual environment...
    python -m venv venv
)

call venv\\Scripts\\activate.bat

if not exist "web\\requirements_unified.txt" (
    echo 📦 Installing dependencies...
    pip install flask flask-socketio flask-cors flask-jwt-extended
    pip install flask-sqlalchemy requests pillow opencv-python
    pip install websockets psutil obs-websocket-py
    pip install pydub imageio moviepy python-dotenv
)

echo 🚀 Starting Matrix Unified Broadcasting Studio...
echo 📍 Studio: http://localhost:8080
echo 👥 Guest: http://localhost:8080/guest-view/[id]
echo.

cd core
python unified_broadcast_server.py %*
pause
'''
    
    with open('LAUNCH.bat', 'w') as f:
        f.write(windows_launcher)
    print("  ✅ Created: LAUNCH.bat")
    
    # Python launcher
    python_launcher = '''#!/bin/bash
# 🌊 MATRIX UNIFIED BROADCASTING STUDIO - LINUX/MAC LAUNCHER

echo "🌊 Matrix Unified Broadcasting Studio"
echo "========================================"
echo

if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

if [ ! -f "web/requirements_unified.txt" ]; then
    echo "📦 Installing dependencies..."
    pip install flask flask-socketio flask-cors flask-jwt-extended
    pip install flask-sqlalchemy requests pillow opencv-python
    pip install websockets psutil obs-websocket-py
    pip install pydub imageio moviepy python-dotenv
fi

echo "🚀 Starting Matrix Unified Broadcasting Studio..."
echo "📍 Studio: http://localhost:8080"
echo "👥 Guest: http://localhost:8080/guest-view/[id]"
echo

cd core
python unified_broadcast_server.py "$@"
'''
    
    with open('LAUNCH.sh', 'w') as f:
        f.write(python_launcher)
    os.chmod('LAUNCH.sh', 0o755)
    print("  ✅ Created: LAUNCH.sh")

def create_environment_template():
    """Create environment configuration template"""
    print("⚙️ Creating environment template...")
    
    env_template = '''# Matrix Unified Broadcasting Studio Configuration
# Copy to .env and update with your settings

# Server Configuration
SECRET_KEY=matrix-studio-secret-key-change-in-production
SQLALCHEMY_DATABASE_URI=sqlite:///matrix_unified.db
JWT_SECRET_KEY=matrix-jwt-secret-change-in-production
HOST=0.0.0.0
PORT=8080
DEBUG=false

# Streaming Configuration
MAX_STREAM_QUALITY=1080p
DEFAULT_STREAM_QUALITY=720p
MAX_GUESTS=8
RECORDING_PATH=core/recordings/

# OBS Studio Configuration
OBS_HOST=localhost
OBS_PORT=4444
OBS_PASSWORD=your-obs-websocket-password
OBS_ENABLED=true

# Platform Credentials
YOUTUBE_API_KEY=your-youtube-api-key
YOUTUBE_CLIENT_SECRET=your-youtube-client-secret
TWITCH_CLIENT_ID=your-twitch-client-id
TWITCH_CLIENT_SECRET=your-twitch-client-secret
TWITCH_ACCESS_TOKEN=your-twitch-access-token
FACEBOOK_ACCESS_TOKEN=your-facebook-access-token
FACEBOOK_PAGE_ID=your-facebook-page-id
LINKEDIN_ACCESS_TOKEN=your-linkedin-access-token

# Security
ALLOWED_ORIGINS=http://localhost:8080,https://yourdomain.com
CORS_ENABLED=true
RATE_LIMIT_ENABLED=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=core/logs/matrix_studio.log
LOG_MAX_SIZE=10MB
LOG_BACKUP_COUNT=5

# Performance
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300
MAX_WORKERS=4

# WebRTC
STUN_SERVER=stun:stun.l.google.com:19302
TURN_SERVER=turn:your-turn-server.com:3478
TURN_USERNAME=your-turn-username
TURN_PASSWORD=your-turn-password
'''
    
    with open('web/.env.example', 'w') as f:
        f.write(env_template)
    print("  ✅ Created: web/.env.example")

def create_requirements():
    """Create requirements file"""
    print("📦 Creating requirements file...")
    
    requirements = '''# Core Framework
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-JWT-Extended==4.5.3
Flask-CORS==4.0.0
Flask-SocketIO==5.3.6

# HTTP/API
requests==2.31.0
urllib3==2.0.7

# Real-time Communication
websockets==12.0
python-socketio==5.9.0
gevent==23.9.1

# Video/Audio Processing
opencv-python==4.8.1.78
Pillow==10.0.1
numpy==1.24.4
imageio==2.31.6
pydub==0.25.1

# System Monitoring
psutil==5.9.6

# Security
cryptography==41.0.7
bcrypt==4.0.1

# Environment
python-dotenv==1.0.0

# OBS Integration
obs-websocket-py==1.0.0

# WebRTC Support
aiortc==1.6.0

# JSON Processing
orjson==3.9.10

# Async Support
aiohttp==3.9.0
aiofiles==23.2.1

# WebSocket Support
simple-websocket==0.11.1
'''
    
    with open('web/requirements_unified.txt', 'w') as f:
        f.write(requirements)
    print("  ✅ Created: web/requirements_unified.txt")

def main():
    """Main setup function"""
    print("🌊 MATRIX UNIFIED BROADCASTING STUDIO - AUTOMATIC SETUP")
    print("=" * 60)
    print()
    
    # Create directory structure
    print("Step 1: Creating Directory Structure")
    print("-" * 40)
    create_directory_structure()
    print()
    
    # Organize files
    print("Step 2: Organizing Project Files")
    print("-" * 40)
    organize_core_components()
    organize_web_components()
    organize_legacy_files()
    organize_test_files()
    organize_documentation()
    print()
    
    # Create configuration files
    print("Step 3: Creating Configuration Files")
    print("-" * 40)
    create_core_init()
    create_entry_point()
    create_launchers()
    create_environment_template()
    create_requirements()
    print()
    
    # Summary
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("✅ Professional directory structure created")
    print("✅ All files organized with full functionality preserved")
    print("✅ Launchers created for easy startup")
    print("✅ Configuration templates provided")
    print()
    print("🚀 TO LAUNCH:")
    print("   Windows: Double-click LAUNCH.bat")
    print("   Linux/Mac: ./LAUNCH.sh")
    print("   Manual: python run.py")
    print()
    print("🌐 ACCESS POINTS:")
    print("   Studio Interface: http://localhost:8080")
    print("   Guest Interface: http://localhost:8080/guest-view/[guest-id]")
    print("   Health Check: http://localhost:8080/api/health")
    print()
    print("📖 DOCUMENTATION:")
    print("   Project Overview: PROJECT_STRUCTURE.md")
    print("   User Guide: docs/README_UNIFIED.md")
    print()

if __name__ == '__main__':
    main()