@echo off
title 🌊 MATRIX STUDIO V2 - STANDALONE LAUNCHER
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                🌊 MATRIX BROADCAST STUDIO V2.0               ║
echo ║                  STANDALONE EDITION                        ║
echo ║                No Docker Required - Native                  ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0matrix-studio"

REM Check Node.js
echo [🔍] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo [❌] Node.js not found! Please install Node.js 18+ first.
    echo [📥] Download from: https://nodejs.org/
    echo.
    echo Opening download page...
    start https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [✅] Node.js found: %NODE_VERSION%

REM Check minimum version
for /f "tokens=1,2 delims=." %%a in ("%NODE_VERSION%") do set NODE_MAJOR=%%a
if %NODE_MAJOR% LSS 18 (
    echo [❌] Node.js version too old! Please install Node.js 18 or higher.
    echo [📥] Current version: %NODE_VERSION%
    echo [📥] Required: Node.js 18+
    echo.
    echo Opening download page...
    start https://nodejs.org/
    pause
    exit /b 1
)

REM Use standalone package.json
echo [📦] Switching to standalone configuration...
if exist "package-standalone.json" (
    copy "package-standalone.json" "package.json" >nul 2>&1
    echo [✅] Standalone configuration activated
) else (
    echo [⚠️] Standalone package not found, using current configuration
)

REM Clear previous installation
echo [🧹] Cleaning previous installation...
if exist "node_modules" rmdir /s /q node_modules >nul 2>&1
if exist "package-lock.json" del package-lock.json >nul 2>&1

REM Install minimal dependencies
echo [📦] Installing minimal dependencies for standalone mode...
echo [⏳] This may take a few moments...

npm install express cors socket.io --no-audit --no-fund >nul 2>&1
if errorlevel 1 (
    echo [❌] Failed to install dependencies!
    echo [💡] Trying alternative installation method...
    npm install express cors socket.io --legacy-peer-deps
    if errorlevel 1 (
        echo [❌] Installation failed completely!
        pause
        exit /b 1
    )
)

echo [✅] Dependencies installed successfully

REM Create directories
echo [📁] Creating directory structure...
if not exist "uploads" mkdir uploads
if not exist "uploads\avatars" mkdir uploads\avatars
if not exist "uploads\scenes" mkdir uploads\scenes
if not exist "uploads\temp" mkdir uploads\temp
if not exist "logs" mkdir logs

echo [✅] Directory structure created

REM Create simple environment
echo [🔧] Creating environment configuration...
(
echo NODE_ENV=standalone
echo PORT=3000
echo LOG_LEVEL=info
echo CORS_ORIGIN=*
) > .env

echo [✅] Environment configured

echo.
echo ════════════════════════════════════════════════════════════════
echo [🚀] STARTING MATRIX STUDIO V2.0 - STANDALONE MODE
echo ════════════════════════════════════════════════════════════════
echo.

echo [⚡] Features Available:
echo ✅ Real-time WebRTC broadcasting
echo ✅ 6 simultaneous guests
echo ✅ 5 professional scene templates  
echo ✅ Enterprise authentication
echo ✅ In-memory database (no setup required)
echo ✅ WebSocket real-time communication
echo ✅ Professional web interface
echo ✅ RESTful API endpoints
echo.

echo [🌐] Services will be available at:
echo 🎯 Main Application:   http://localhost:3000
echo 📊 Health Check:       http://localhost:3000/health
echo 🔌 API Endpoints:      http://localhost:3000/api
echo ⚡ WebSocket:          ws://localhost:3000
echo.

echo [👤] Demo Login Credentials:
echo 📧 Email:    demo@matrixstudio.com
echo 🔑 Password:  demo123
echo.

echo ════════════════════════════════════════════════════════════════
echo [🎮] COMMANDS AFTER START:
echo ════════════════════════════════════════════════════════════════
echo.
echo 🛑 Stop Server:      Press Ctrl+C in this window
echo 🔄 Restart:          Close and run this launcher again
echo 📋 View Logs:        Check console output below
echo 🌐 Access Web UI:    Open http://localhost:3000 in browser
echo.

echo [🎯] Press any key to start the standalone server...
pause >nul

echo.
echo [🔍] Final system check...
if exist "src\standalone-server.js" (
    echo [✅] Standalone server found
) else (
    echo [❌] Standalone server not found!
    pause
    exit /b 1
)

if exist "src\services\introOutro.js" (
    echo [✅] Intro/Outro system found
) else (
    echo [⚠️] Intro/Outro system not available
)

echo.
echo ══════════════════════════════════════════════════════════════
echo [🚀] LAUNCHING MATRIX STUDIO V2.0 - STANDALONE MODE
echo ══════════════════════════════════════════════════════════════
echo.

echo [⚡] Initializing Matrix Broadcast Studio...
echo [🎯] Starting server with command: node src/standalone-server.js
echo.

REM Start the standalone server with error handling
node src/standalone-server.js
if errorlevel 1 (
    echo.
    echo [❌] Server failed to start!
    echo [💡] Common issues:
    echo [💡] 1. Port 3000 already in use
    echo [💡] 2. Missing dependencies
    echo [💡] 3. Corrupted installation
    echo.
    echo [🔧] Troubleshooting:
    echo [🔧] - Check if port 3000 is free: netstat -an | findstr ":3000"
    echo [🔧] - Clear cache: npm cache clean --force
    echo [🔧] - Reinstall: npm install
    echo.
    pause
    exit /b 1
)

echo.
echo [⚠️] Server stopped gracefully.
echo [💡] To restart, run this launcher again.
echo [💡] To check logs, review console output above.
echo.
echo [🌊] Thank you for using Matrix Broadcast Studio!
pause >nul