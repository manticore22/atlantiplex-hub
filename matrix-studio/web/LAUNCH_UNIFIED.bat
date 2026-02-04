@echo off
REM 🌊 Matrix Unified Broadcasting Server Launcher
REM Professional multi-platform streaming with real-time capabilities

echo.
echo ========================================
echo 🌊 MATRIX UNIFIED BROADCASTING SERVER
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo 🐍 Python detected: 
python --version

REM Check if virtual environment exists
if not exist "venv" (
    echo 🔧 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
echo 📦 Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed
)

REM Check if OBS is running (optional)
echo 🔍 Checking OBS connection...
tasklist /FI "IMAGENAME eq obs64.exe" 2>NUL | find /I "obs64.exe" >NUL
if errorlevel 1 (
    echo ⚠️  OBS Studio is not running
    echo OBS Studio is optional but recommended for full functionality
    echo.
    set /p choice="Do you want to continue without OBS? (y/n): "
    if /i not "%choice%"=="y" (
        echo Launching OBS Studio...
        start "" "obs64.exe" 2>nul || echo ⚠️  OBS Studio not found in system PATH
        echo Waiting for OBS to start...
        timeout /t 5 >nul
    )
) else (
    echo ✅ OBS Studio is running
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads
if not exist "templates" mkdir templates

REM Check for FFmpeg
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  FFmpeg not found in PATH
    echo FFmpeg is recommended for transcoding capabilities
    echo Please install FFmpeg and add to system PATH
) else (
    echo ✅ FFmpeg detected
)

REM Start the unified server
echo.
echo 🚀 Starting Matrix Unified Broadcasting Server...
echo.
echo 📱 Studio Interface: http://localhost:8080
echo 👥 Guest View: http://localhost:8080/guest-view/[guest-id]
echo 📊 Health Check: http://localhost:8080/api/health
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Check command line arguments
if "%1"=="--debug" (
    echo 🔍 Debug mode enabled
    set DEBUG=1
    python unified_broadcast_server.py
) else if "%1"=="--init-db" (
    echo 🗄️  Initializing database...
    python -c "from unified_broadcast_server import app, db; app.app_context().push(); db.create_all(); print('✅ Database initialized')"
    echo.
    echo Database initialized successfully
    echo You can now run the server with: launch_unified.bat
    pause
) else (
    python unified_broadcast_server.py
)

if errorlevel 1 (
    echo.
    echo ❌ Server encountered an error
    echo Check logs/unified_server.log for details
    pause
)

echo.
echo Server stopped
pause