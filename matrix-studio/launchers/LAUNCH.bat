@echo off
REM 🌊 MATRIX UNIFIED BROADCASTING STUDIO - PROFESSIONAL LAUNCHER
REM Complete one-click launch with full functionality preservation

title Matrix Unified Broadcasting Studio

REM Set working directory
cd /d "%~dp0"

REM === VISUAL SETUP ===
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║   🌊 MATRIX UNIFIED BROADCASTING STUDIO v2.0                     ║
echo ║                                                              ║
echo ║   Professional Multi-Platform Streaming Platform                   ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM === CLEANUP AND ORGANIZATION ===
echo 🔧 Step 1: Project Structure Cleanup & Organization
echo --------------------------------------------------------------
echo.

REM Create proper directory structure if doesn't exist
if not exist "core" mkdir core
if not exist "core\logs" mkdir core\logs
if not exist "core\uploads" mkdir core\uploads
if not exist "core\recordings" mkdir core\recordings
if not exist "web" mkdir web
if not exist "web\templates" mkdir web\templates
if not exist "web\static" mkdir web\static
if not exist "tests" mkdir tests
if not exist "docs" mkdir docs
if not exist "legacy" mkdir legacy

REM Move any misplaced files to proper locations
echo   📁 Organizing project files...
if exist "unified_broadcast_server.py" move unified_broadcast_server.py core\
if exist "comprehensive_api.py" move comprehensive_api.py core\
if exist "broadcast_engine.py" move broadcast_engine.py core\
if exist "guest_management.py" move guest_management.py core\
if exist "scene_manager.py" move scene_manager.py core\
if exist "platform_integrations.py" move platform_integrations.py core\
if exist "obs_integration.py" move obs_integration.py core\
if exist "analytics.py" move analytics.py core\
if exist "scheduler.py" move scheduler.py core\
if exist "requirements.txt" move requirements.txt web\
if exist "requirements_unified.txt" move requirements_unified.txt web\
if exist "templates\*.html" move templates\*.html web\templates\
if exist "public\*.html" move public\*.html web\static\
if exist "templates" xcopy /e /i templates web\templates\*.*
if exist "public" xcopy /e /i public web\static\*.*

REM Move legacy files
echo   🗄️  Archiving legacy files...
for %%f in (*.md legacy_files batch_files config_files) do (
    if exist "%%f" move %%f legacy\
)

REM Move cache and temp files to legacy
if exist "__pycache__" move __pycache__ legacy\
if exist "node_modules" move node_modules legacy\
if exist "*.pyc" move *.pyc legacy\

echo   ✅ Project structure organized

REM === ENVIRONMENT CHECK ===
echo.
echo 🔍 Step 2: Environment Verification
echo --------------------------------------------------------------
echo.

REM Check Python
echo   🐍 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo   ❌ Python not found!
    echo   📥 Download Python 3.8+ from: https://python.org
    echo.
    echo   Press any key to open Python download page...
    pause >nul
    start https://python.org/downloads/
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo   ✅ Python found: %PYTHON_VERSION%
)

REM Check FFmpeg
echo   🎬 Checking FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo   ⚠️  FFmpeg not found in PATH
    echo   📥 FFmpeg is recommended for optimal streaming
    echo   📥 Download from: https://ffmpeg.org/download.html
    set FFMPEG_AVAILABLE=false
) else (
    echo   ✅ FFmpeg available
    set FFMPEG_AVAILABLE=true
)

REM Check OBS Studio
echo   📺 Checking OBS Studio...
tasklist /FI "IMAGENAME eq obs64.exe" 2>NUL | find /I "obs64.exe" >NUL
if errorlevel 1 (
    echo   ⚠️  OBS Studio not running
    echo   💡 OBS Studio is optional but recommended for full functionality
    echo   📥 Download from: https://obsproject.com
    set OBS_RUNNING=false
) else (
    echo   ✅ OBS Studio is running
    set OBS_RUNNING=true
)

REM === VIRTUAL ENVIRONMENT ===
echo.
echo 🐍 Step 3: Python Virtual Environment Setup
echo --------------------------------------------------------------
echo.

if not exist "venv" (
    echo   🔧 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo   ❌ Failed to create virtual environment
        echo   💡 Try running as Administrator or check Python installation
        pause
        exit /b 1
    )
    echo   ✅ Virtual environment created
) else (
    echo   ✅ Virtual environment exists
)

echo   🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM === DEPENDENCY INSTALLATION ===
echo.
echo 📦 Step 4: Python Dependencies Installation
echo --------------------------------------------------------------
echo.

echo   📦 Checking and installing dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo   📥 Installing dependencies (this may take a few minutes)...
    pip install --upgrade pip >nul 2>&1
    
    REM Install from unified requirements if available
    if exist "web\requirements_unified.txt" (
        pip install -r web\requirements_unified.txt
    ) else (
        echo   📥 Installing core dependencies...
        pip install flask flask-socketio flask-cors flask-jwt-extended
        pip install flask-sqlalchemy requests pillow opencv-python
        pip install websockets psutil obs-websocket-py aiortc
        pip install pydub imageio moviepy python-dotenv
        pip install google-api-python-client google-auth google-auth-oauthlib
    )
    
    if errorlevel 1 (
        echo   ❌ Failed to install dependencies
        echo   💡 Check internet connection and try running as Administrator
        pause
        exit /b 1
    )
    echo   ✅ Dependencies installed successfully
) else (
    echo   ✅ Dependencies already installed
)

REM === CONFIGURATION ===
echo.
echo ⚙️  Step 5: Configuration Setup
echo --------------------------------------------------------------
echo.

if not exist "web\.env" (
    if exist "web\.env.example" (
        echo   📋 Creating environment configuration...
        copy web\.env.example web\.env >nul 2>&1
        echo   ✅ Environment file created from template
        echo   💡 Edit web\.env to configure platform credentials
    ) else (
        echo   🔧 Creating default configuration...
        (
        echo # Matrix Unified Broadcasting Studio Configuration
        echo SECRET_KEY=matrix-studio-secret-key-%RANDOM%
        echo SQLALCHEMY_DATABASE_URI=sqlite:///matrix_unified.db
        echo JWT_SECRET_KEY=matrix-jwt-secret-%RANDOM%
        echo HOST=0.0.0.0
        echo PORT=8080
        echo DEBUG=false
        echo MAX_GUESTS=8
        echo DEFAULT_QUALITY=720p
        echo LOG_LEVEL=INFO
        echo OBS_ENABLED=true
        echo OBS_HOST=localhost
        echo OBS_PORT=4444
        echo OBS_PASSWORD=
        echo YOUTUBE_API_KEY=
        echo TWITCH_CLIENT_ID=
        echo FACEBOOK_ACCESS_TOKEN=
        echo LINKEDIN_ACCESS_TOKEN=
        echo WEBRTC_STUN_SERVER=stun:stun.l.google.com:19302
        echo CORS_ENABLED=true
        echo ALLOWED_ORIGINS=http://localhost:8080
        ) > web\.env
        echo   ✅ Default configuration created
    )
) else (
    echo   ✅ Configuration file exists
)

REM === DATABASE SETUP ===
echo.
echo 🗄️  Step 6: Database Initialization
echo --------------------------------------------------------------
echo.

echo   🔧 Initializing database...
python -c "
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
try:
    from unified_broadcast_server import app, db
    with app.app_context():
        db.create_all()
        print('✅ Database initialized successfully')
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
    sys.exit(1)
"

if errorlevel 1 (
    echo   ❌ Database initialization failed
    echo   💡 Check configuration and permissions
    pause
    exit /b 1
)

REM === SERVICE CHECKS ===
echo.
echo 🔍 Step 7: Service Health Checks
echo --------------------------------------------------------------
echo.

REM Check network connectivity
echo   🌐 Checking network connectivity...
ping -n 1 google.com >nul 2>&1
if errorlevel 1 (
    echo   ⚠️  No internet connection (some features may be limited)
    set INTERNET_AVAILABLE=false
) else (
    echo   ✅ Internet connection available
    set INTERNET_AVAILABLE=true
)

REM Check available ports
echo   🔌 Checking port availability...
netstat -an | find ":8080" >nul 2>&1
if errorlevel 1 (
    echo   ✅ Port 8080 is available
) else (
    echo   ⚠️  Port 8080 may be in use
    echo   💡 The server will try to start anyway
)

REM === LAUNCH OPTIONS ===
echo.
echo 🚀 Step 8: Launch Configuration
echo --------------------------------------------------------------
echo.

REM Check for command line arguments
if "%1"=="--debug" (
    set DEBUG_MODE=true
    echo   🔍 Debug mode enabled
) else (
    set DEBUG_MODE=false
)

if "%1"=="--no-obs" (
    set NO_OBS=true
    echo   📺 OBS Studio integration disabled
) else (
    set NO_OBS=false
)

if "%1"=="--test" (
    set TEST_MODE=true
    echo   🧪 Test mode enabled
) else (
    set TEST_MODE=false
)

REM === PRE-LAUNCH SUMMARY ===
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    SYSTEM STATUS SUMMARY                        ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║  🐍 Python: %PYTHON_VERSION%                                      ║
echo ║  🎬 FFmpeg: %FFMPEG_AVAILABLE%                                   ║
echo ║  📺 OBS Studio: %OBS_RUNNING%                                    ║
echo ║  🌐 Internet: %INTERNET_AVAILABLE%                                 ║
echo ║  🐍 Virtual Env: Active                                         ║
echo ║  📦 Dependencies: Installed                                        ║
echo ║  🗄️  Database: Ready                                              ║
echo ║  ⚙️  Configuration: Loaded                                          ║
echo ║  🐛 Debug Mode: %DEBUG_MODE%                                      ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

if "%TEST_MODE%"=="true" (
    echo 🧪 Running in test mode - will start server and run tests
    pause
) else (
    echo 🌊 Ready to launch Matrix Unified Broadcasting Studio!
    echo.
    echo 📍 Server will be available at:
    echo    📺 Studio Interface: http://localhost:8080
    echo    👥 Guest Interface:  http://localhost:8080/guest-view/[guest-id]
    echo    📊 Health Check:     http://localhost:8080/api/health
    echo    📖 Documentation:    docs/README_UNIFIED.md
    echo.
    echo 💡 Press Ctrl+C to stop the server
    echo.
)

REM === LAUNCH SERVER ===
echo 🚀 Step 9: Starting Unified Broadcasting Server
echo ================================================================================

if "%TEST_MODE%"=="true" (
    REM Run tests first
    echo 🧪 Running tests...
    python -m pytest tests/ -v
    
    if errorlevel 1 (
        echo ❌ Some tests failed
    ) else (
        echo ✅ All tests passed
    )
    
    echo.
    echo 🚀 Starting server after tests...
    pause
)

REM Change to core directory for imports
cd core

REM Start the server
if "%DEBUG_MODE%"=="true" (
    echo 🔍 Starting in DEBUG mode...
    python unified_broadcast_server.py
) else (
    echo 🌊 Starting production server...
    python unified_broadcast_server.py
)

REM === POST-LAUNCH ===
if errorlevel 1 (
    echo.
    echo ❌ Server encountered an error during startup
    echo 🔍 Check the following:
    echo    📄 Logs: core/logs/matrix_studio.log
    echo    ⚙️  Configuration: web/.env
    echo    🔌 Port availability: Check if port 8080 is free
    echo    📦 Dependencies: Ensure all packages are installed
    echo.
    echo 💡 Try running with debug mode: START.bat --debug
    echo.
    pause
) else (
    echo.
    echo ✅ Server stopped normally
    echo 📊 Check logs for session information: core/logs/matrix_studio.log
    echo.
    pause
)

REM Return to project root
cd /d "%~dp0"

echo.
echo 🌊 Matrix Unified Broadcasting Studio - Session Complete
echo ================================================================================