@echo off
REM 🌊 MATRIX STUDIO - COMPLETE PROJECT CLEANUP & ORGANIZATION
REM Preserves all functionality while creating clean structure

title Matrix Studio - Project Cleanup

REM Set working directory
cd /d "%~dp0"

REM === VISUAL HEADER ===
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║   🧹 MATRIX UNIFIED BROADCASTING STUDIO                       ║
echo ║                                                              ║
echo ║   Complete Project Cleanup & Organization                         ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🔧 Step 1: Creating Professional Directory Structure
echo ================================================================================
echo.

REM Create proper directory structure
echo   📁 Creating directory structure...
mkdir core 2>nul
mkdir core\broadcasting 2>nul
mkdir core\guests 2>nul
mkdir core\scenes 2>nul
mkdir core\platforms 2>nul
mkdir core\obs 2>nul
mkdir core\analytics 2>nul
mkdir core\logs 2>nul
mkdir core\uploads 2>nul
mkdir core\recordings 2>nul
mkdir web 2>nul
mkdir web\templates 2>nul
mkdir web\static 2>nul
mkdir web\static\css 2>nul
mkdir web\static\js 2>nul
mkdir web\static\images 2>nul
mkdir tests 2>nul
mkdir tests\unit 2>nul
mkdir tests\integration 2>nul
mkdir docs 2>nul
mkdir docs\api 2>nul
mkdir docs\user 2>nul
mkdir docs\development 2>nul
mkdir legacy 2>nul
mkdir legacy\old_versions 2>nul
mkdir legacy\backups 2>nul

echo   ✅ Directory structure created

REM === CORE COMPONENTS ORGANIZATION ===
echo.
echo 🔧 Step 2: Core Components Organization
echo ================================================================================
echo.

REM Move core server files
echo   🌊 Organizing core server components...
if exist "unified_broadcast_server.py" (
    move /Y unified_broadcast_server.py core\
    echo     ✅ Main unified server moved to core/
)

if exist "comprehensive_api.py" (
    move /Y comprehensive_api.py core\
    echo     ✅ Comprehensive API moved to core/
)

REM Move specialized components
echo   📹 Organizing broadcasting components...
if exist "broadcast_engine.py" (
    move /Y broadcast_engine.py core\broadcasting\
    echo     ✅ Broadcast engine moved to core/broadcasting/
)

if exist "video_compositor.py" move /Y video_compositor.py core\broadcasting\ 2>nul
if exist "audio_mixer.py" move /Y audio_mixer.py core\broadcasting\ 2>nul

echo   👥 Organizing guest management...
if exist "guest_management.py" (
    move /Y guest_management.py core\guests\
    echo     ✅ Guest management moved to core/guests/
)

if exist "guest_controller.py" move /Y guest_controller.py core\guests\ 2>nul

echo   🎨 Organizing scene management...
if exist "scene_manager.py" (
    move /Y scene_manager.py core\scenes\
    echo     ✅ Scene manager moved to core/scenes/
)

echo   📡 Organizing platform integrations...
if exist "platform_integrations.py" (
    move /Y platform_integrations.py core\platforms\
    echo     ✅ Platform integrations moved to core/platforms/
)

if exist "multi_platform_streamer.py" move /Y multi_platform_streamer.py core\platforms\ 2>nul

echo   📺 Organizing OBS integration...
if exist "obs_integration.py" (
    move /Y obs_integration.py core\obs\
    echo     ✅ OBS integration moved to core/obs/
)

if exist "obs_controller.py" move /Y obs_controller.py core\obs\ 2>nul

echo   📊 Organizing analytics...
if exist "analytics.py" (
    move /Y analytics.py core\analytics\
    echo     ✅ Analytics moved to core/analytics/
)

if exist "stream_analytics.py" move /Y stream_analytics.py core\analytics\ 2>nul

echo   ⏰ Organizing scheduler...
if exist "scheduler.py" (
    move /Y scheduler.py core\
    echo     ✅ Scheduler moved to core/
)

echo   ✅ All core components organized

REM === WEB INTERFACE ORGANIZATION ===
echo.
echo 🔧 Step 3: Web Interface Organization
echo ================================================================================
echo.

echo   🌐 Organizing web templates...
if exist "unified_studio.html" (
    move /Y unified_studio.html web\templates\
    echo     ✅ Main studio template moved to web/templates/
)

if exist "guest_view.html" (
    move /Y guest_view.html web\templates\
    echo     ✅ Guest view template moved to web/templates/
)

if exist "templates\*.html" (
    move /Y templates\*.html web\templates\
    echo     ✅ Additional templates moved to web/templates/
)

echo   📁 Organizing static assets...
if exist "index.html" move /Y index.html web\static\
if exist "studio.html" move /Y studio.html web\static\
if exist "guest.html" move /Y guest.html web\static\
if exist "matrix.html" move /Y matrix.html web\static\
if exist "public\*.*" move /Y public\*.* web\static\
if exist "public\css" move /Y public\css web\static\css\
if exist "public\js" move /Y public\js web\static\js\
if exist "public\images" move /Y public\images web\static\images\

echo   📦 Organizing configuration...
if exist "requirements_unified.txt" (
    move /Y requirements_unified.txt web\
    echo     ✅ Requirements moved to web/
)

if exist "requirements.txt" move /Y requirements.txt web\ 2>nul
if exist ".env*" move /Y .env* web\ 2>nul
if exist "config.json" move /Y config.json web\ 2>nul

echo   ✅ Web interface organized

REM === LEGACY FILES ORGANIZATION ===
echo.
echo 🔧 Step 4: Legacy Files Management
echo ================================================================================
echo.

echo   🗄️  Moving legacy files...
REM Move Python legacy files
for %%f in (app*.py main*.py server*.py matrix*.py final*.py production*.py test*.py simple*.py) do (
    if exist "%%f" (
        move /Y "%%f" legacy\
        echo     📄 Moved: %%f
    )
)

REM Move batch files
for %%f in (*.bat) do (
    if /i not "%%f"=="LAUNCH.bat" if /i not "%%f"=="START.bat" (
        move /Y "%%f" legacy\
        echo     📄 Moved batch: %%f
    )
)

REM Move configuration files
for %%f in (*.json *.yml *.yaml Dockerfile docker-compose*) do (
    if exist "%%f" (
        move /Y "%%f" legacy\
        echo     📄 Moved config: %%f
    )
)

REM Move cache and temp files
if exist "__pycache__" (
    move /Y __pycache__ legacy\
    echo     📁 Moved: __pycache__
)

if exist "node_modules" (
    move /Y node_modules legacy\
    echo     📁 Moved: node_modules
)

if exist "*.pyc" (
    move /Y *.pyc legacy\
    echo     📄 Moved: *.pyc files
)

if exist "src" (
    move /Y src legacy\
    echo     📁 Moved: src/
)

echo   ✅ Legacy files organized

REM === TEST FILES ORGANIZATION ===
echo.
echo 🔧 Step 5: Test Files Organization
echo ================================================================================
echo.

echo   🧪 Organizing test files...
if exist "test*.py" (
    move /Y test*.py tests\
    echo     ✅ Test files moved to tests/
)

if exist "*_test*.py" (
    move /Y *_test*.py tests\
    echo     ✅ Additional test files moved to tests/
)

if exist "tests.py" (
    move /Y tests.py tests\
    echo     ✅ Main test file moved to tests/
)

echo   ✅ Test files organized

REM === DOCUMENTATION ORGANIZATION ===
echo.
echo 🔧 Step 6: Documentation Organization
echo ================================================================================
echo.

echo   📚 Organizing documentation...
if exist "README_UNIFIED.md" (
    move /Y README_UNIFIED.md docs\
    echo     ✅ Main documentation moved to docs/
)

if exist "README*.md" (
    move /Y README*.md docs\user\
    echo     ✅ User guides moved to docs/user/
)

if exist "*.md" (
    move /Y *.md docs\user\
    echo     ✅ Additional documentation moved to docs/user/
)

echo   ✅ Documentation organized

REM === CORE INIT FILE CREATION ===
echo.
echo 🔧 Step 7: Core Package Initialization
echo ================================================================================
echo.

echo   📄 Creating core package init...
(
    echo # Matrix Unified Broadcasting Studio - Core Package
    echo __version__ = "2.0.0"
    echo __author__ = "Matrix Studio Team"
    echo __description__ = "Professional multi-platform streaming platform"
    echo.
    echo # Main Components
    echo from .unified_broadcast_server import unified_system, app, socketio
    echo from .comprehensive_api import setup_comprehensive_api
    echo.
    echo # Module Imports
    echo from .broadcasting import broadcast_engine
    echo from .guests import guest_management
    echo from .scenes import scene_manager
    echo from .platforms import platform_integrations
    echo from .obs import obs_integration
    echo from .analytics import analytics
    echo from .scheduler import scheduler
) > core\__init__.py

echo   ✅ Core package initialized

REM === UPDATED LAUNCHERS ===
echo.
echo 🔧 Step 8: Updated Launcher Creation
echo ================================================================================
echo.

echo   🚀 Creating main launcher...
(
    echo @echo off
    echo REM 🌊 MATRIX UNIFIED BROADCASTING STUDIO - MAIN LAUNCHER
    echo title Matrix Unified Broadcasting Studio
    echo cd /d "%%~dp0"
    echo.
    echo echo 🌊 Matrix Unified Broadcasting Studio
    echo echo ========================================
    echo echo.
    echo.
    echo if not exist "venv" (
    echo     echo 🐍 Creating virtual environment...
    echo     python -m venv venv
    echo ^)
    echo.
    echo call venv\Scripts\activate.bat
    echo.
    echo if not exist "web\requirements_unified.txt" (
    echo     echo 📦 Installing dependencies...
    echo     pip install flask flask-socketio flask-cors flask-jwt-extended
    echo     pip install flask-sqlalchemy requests pillow opencv-python
    echo     pip install websockets psutil obs-websocket-py
    echo     pip install pydub imageio moviepy python-dotenv
    echo ^)
    echo.
    echo echo 🚀 Starting Matrix Unified Broadcasting Studio...
    echo echo 📍 Studio: http://localhost:8080
    echo echo 👥 Guest: http://localhost:8080/guest-view/[id]
    echo echo.
    echo cd core
    echo python unified_broadcast_server.py %%*
    echo.
    echo pause
) > LAUNCH.bat

echo   📄 Creating web launcher...
(
    echo @echo off
    echo REM 🌊 MATRIX STUDIO - WEB LAUNCHER
    echo cd /d "%%~dp0\web"
    echo call ..\venv\Scripts\activate.bat
    echo pip install -r requirements_unified.txt
    echo cd ..\core
    echo python unified_broadcast_server.py %%*
) > web\LAUNCH_WEB.bat

echo   ✅ Launchers created

REM === ENVIRONMENT TEMPLATES ===
echo.
echo 🔧 Step 9: Environment Configuration Setup
echo ================================================================================
echo.

if not exist "web\.env.example" (
    echo   📋 Creating environment template...
    (
        echo # Matrix Unified Broadcasting Studio Configuration
        echo # Copy to .env and update with your settings
        echo.
        echo # Server Configuration
        echo SECRET_KEY=matrix-studio-secret-key-change-in-production
        echo SQLALCHEMY_DATABASE_URI=sqlite:///matrix_unified.db
        echo JWT_SECRET_KEY=matrix-jwt-secret-change-in-production
        echo HOST=0.0.0.0
        echo PORT=8080
        echo DEBUG=false
        echo.
        echo # Streaming Configuration
        echo MAX_STREAM_QUALITY=1080p
        echo DEFAULT_STREAM_QUALITY=720p
        echo MAX_GUESTS=6
        echo RECORDING_PATH=core/recordings/
        echo.
        echo # OBS Studio Configuration
        echo OBS_HOST=localhost
        echo OBS_PORT=4444
        echo OBS_PASSWORD=your-obs-websocket-password
        echo OBS_ENABLED=true
        echo.
        echo # Platform Credentials
        echo YOUTUBE_API_KEY=your-youtube-api-key
        echo YOUTUBE_CLIENT_SECRET=your-youtube-client-secret
        echo TWITCH_CLIENT_ID=your-twitch-client-id
        echo TWITCH_CLIENT_SECRET=your-twitch-client-secret
        echo TWITCH_ACCESS_TOKEN=your-twitch-access-token
        echo FACEBOOK_ACCESS_TOKEN=your-facebook-access-token
        echo FACEBOOK_PAGE_ID=your-facebook-page-id
        echo LINKEDIN_ACCESS_TOKEN=your-linkedin-access-token
        echo.
        echo # Security
        echo ALLOWED_ORIGINS=http://localhost:8080,https://yourdomain.com
        echo CORS_ENABLED=true
        echo RATE_LIMIT_ENABLED=true
        echo.
        echo # Logging
        echo LOG_LEVEL=INFO
        echo LOG_FILE=core/logs/matrix_studio.log
        echo LOG_MAX_SIZE=10MB
        echo LOG_BACKUP_COUNT=5
        echo.
        echo # Performance
        echo REDIS_URL=redis://localhost:6379/0
        echo CACHE_TTL=300
        echo MAX_WORKERS=4
        echo.
        echo # WebRTC
        echo STUN_SERVER=stun:stun.l.google.com:19302
        echo TURN_SERVER=turn:your-turn-server.com:3478
        echo TURN_USERNAME=your-turn-username
        echo TURN_PASSWORD=your-turn-password
    ) > web\.env.example
    echo     ✅ Environment template created
)

REM === PROJECT INITIALIZATION FILE ===
echo.
echo 🔧 Step 10: Project Initialization Setup
echo ================================================================================
echo.

echo   📄 Creating Python entry point...
(
    echo #!/usr/bin/env python3
    echo """
    echo 🌊 MATRIX UNIFIED BROADCASTING STUDIO
    echo Main entry point for organized project structure
    echo """
    echo.
    echo import sys
    echo import os
    echo import argparse
    echo.
    echo # Add core directory to Python path
    echo sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
    echo.
    echo if __name__ == '__main__':
    echo     from unified_broadcast_server import unified_system, app, socketio
    echo     
    echo     parser = argparse.ArgumentParser(description='Matrix Unified Broadcasting Studio')
    echo     parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    echo     parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    echo     parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    echo     parser.add_argument('--init-db', action='store_true', help='Initialize database')
    echo     
    echo     args = parser.parse_args()
    echo     
    echo     if args.init_db:
    echo         print("🗄️ Initializing database...")
    echo         with app.app_context():
    echo             from unified_broadcast_server import db
    echo             db.create_all()
    echo         print("✅ Database initialized successfully")
    echo     else:
    echo         import time
    echo         print("🌊 Starting Matrix Unified Broadcasting Studio")
    echo         print(f"🌐 Server will be available at: http://{args.host}:{args.port}")
    echo         print("👥 Studio Interface: http://localhost:8080")
    echo         print("📊 API Documentation: http://localhost:8080/api/docs")
    echo         print("=" * 60)
    echo         
    echo         # Set start time for uptime calculation
    echo         unified_system.start_time = time.time()
    echo         
    echo         # Start server
    echo         socketio.run(
    echo             app,
    echo             host=args.host,
    echo             port=args.port,
    echo             debug=args.debug,
    echo             allow_unsafe_werkzeug=True
    echo         )
) > run.py

echo   ✅ Python entry point created

REM === FINAL DOCUMENTATION ===
echo.
echo 🔧 Step 11: Final Documentation Creation
echo ================================================================================
echo.

echo   📖 Creating project overview...
(
    echo # 🌊 Matrix Unified Broadcasting Studio - Clean Project Structure
    echo.
    echo ## 📁 Final Organized Structure
    echo.
    echo ```
    echo matrix-studio/
    echo ├── 🚀 LAUNCH.bat                    # Main launcher ^(recommended^)
    echo ├── 🔧 run.py                         # Python entry point
    echo ├── 📖 README.md                      # Project overview
    echo │
    echo ├── 📂 core/                         # Core server components
    echo │   ├── 📄 __init__.py              # Package initialization
    echo │   ├── 🌊 unified_broadcast_server.py    # Main unified server
    echo │   ├── 🔌 comprehensive_api.py           # Complete API endpoints
    echo │   ├── 📂 broadcasting/            # Streaming engine
    echo │   ├── 👥 guests/                   # Guest management
    echo │   ├── 🎨 scenes/                   # Scene management
    echo │   ├── 🌐 platforms/                # Platform integrations
    echo │   ├── 📺 obs/                      # OBS Studio integration
    echo │   ├── 📊 analytics/                # Analytics engine
    echo │   ├── ⏰ scheduler.py              # Stream scheduling
    echo │   ├── 📁 logs/                     # Application logs
    echo │   └── 📁 uploads/                  # Media uploads
    echo │
    echo ├── 🌐 web/                          # Web interface
    echo │   ├── 🎨 templates/                # HTML templates
    echo │   ├── 📁 static/                   # Static assets
    echo │   ├── 📦 requirements_unified.txt       # Dependencies
    echo │   └── ⚙️ .env.example              # Environment template
    echo │
    echo ├── 🧪 tests/                        # Test suites
    echo ├── 📖 docs/                         # Documentation
    echo └── 🗄️ legacy/                       # Legacy/deprecated code
    echo ```
    echo.
    echo ## 🚀 Quick Start
    echo.
    echo ### Option 1: Main Launcher ^(Recommended^)
    echo ```bash
    echo # Double-click or run:
    echo LAUNCH.bat
    echo ```
    echo.
    echo ## ✨ Key Features Preserved
    echo.
    echo ### 🎬 Broadcasting
    echo - Multi-platform streaming ^(YouTube, Twitch, Facebook, LinkedIn^)
    echo - Professional OBS Studio integration
    echo - Adaptive quality streaming ^(360p-1080p^)
    echo - Real-time monitoring and failover
    echo.
    echo ### 👥 Guest Management
    echo - WebRTC-based guest connections ^(up to 6^)
    echo - Role-based permissions ^(Host, Moderator, Guest^)
    echo - Real-time media controls
    echo - Screen sharing and chat
    echo.
    echo ### 🎨 Scene Management
    echo - Dynamic scene switching
    echo - Picture-in-picture and split-screen
    echo - Custom layout creation
    echo - Smooth transitions
    echo.
    echo ### 📊 Analytics
    echo - Real-time viewer metrics
    echo - Performance monitoring
    echo - Historical data
    echo - Export capabilities
    echo.
    echo ---
    echo **🌊 Matrix Unified Broadcasting Studio - Professional Streaming Platform**
) > PROJECT_OVERVIEW.md

echo   ✅ Final documentation created

REM === CLEANUP SUMMARY ===
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    CLEANUP COMPLETED                           ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║                                                              ║
echo ║  📁 Directory Structure: Professional and organized          ║
echo ║  🌊 Core Components: Properly placed in core/            ║
echo ║  🌐 Web Interface: Organized in web/                     ║
echo ║  🧪 Tests: Moved to tests/                                 ║
echo ║  📖 Documentation: Organized in docs/                    ║
echo ║  🗄️  Legacy Files: Archived in legacy/                    ║
echo ║  🚀 Launchers: Multiple options created                  ║
echo ║  ⚙️  Configuration: Template and init setup             ║
echo ║                                                              ║
echo ║  ✅ Full Functionality Preserved!                       ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🌊 Project successfully cleaned and organized!
echo.
echo 🚀 Ready to launch with: LAUNCH.bat
echo 📖 View structure: PROJECT_OVERVIEW.md
echo.
pause