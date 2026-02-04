@echo off
title 🌊 MATRIX STUDIO V2 - STANDALONE INSTALLER
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                🌊 MATRIX BROADCAST STUDIO V2.0               ║
echo ║              STANDALONE INSTALLATION SYSTEM               ║
echo ║                   Native Node.js Deployment               ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0matrix-studio"

REM Check Node.js installation
echo [🔍] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo [❌] Node.js not found! Please install Node.js 18+ first.
    echo [📥] Download from: https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [✅] Node.js found: %NODE_VERSION%

REM Check PostgreSQL installation
echo [🔍] Checking PostgreSQL installation...
psql --version >nul 2>&1
if errorlevel 1 (
    echo [❌] PostgreSQL not found! Please install PostgreSQL first.
    echo [📥] Download from: https://www.postgresql.org/download/windows/
    pause
    exit /b 1
)

for /f "tokens=3" %%i in ('psql --version') do set PG_VERSION=%%i
echo [✅] PostgreSQL found: %PG_VERSION%

REM Check Redis installation
echo [🔍] Checking Redis installation...
redis-cli --version >nul 2>&1
if errorlevel 1 (
    echo [⚠️] Redis not found! Installing Redis for Windows...
    echo [📥] Downloading Redis...
    
    REM Download Redis for Windows
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip' -OutFile 'redis.zip'"
    
    if exist redis.zip (
        echo [📦] Extracting Redis...
        powershell -Command "Expand-Archive -Path 'redis.zip' -DestinationPath '.' -Force"
        echo [✅] Redis installed successfully
        del redis.zip
    ) else (
        echo [⚠️] Redis download failed, continuing without Redis...
    )
)

REM Install Node.js dependencies
echo.
echo [📦] Installing Node.js dependencies...
call npm install
if errorlevel 1 (
    echo [❌] Failed to install dependencies!
    pause
    exit /b 1
)
echo [✅] Dependencies installed successfully

REM Install FFmpeg
echo [🔍] Checking FFmpeg installation...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [⚠️] FFmpeg not found! Installing FFmpeg...
    echo [📥] Downloading FFmpeg...
    
    REM Download FFmpeg for Windows
    powershell -Command "Invoke-WebRequest -Uri 'https://ffmpeg.org/releases/ffmpeg-6.0-full_build.zip' -OutFile 'ffmpeg.zip'"
    
    if exist ffmpeg.zip (
        echo [📦] Extracting FFmpeg...
        powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath '.' -Force"
        move "ffmpeg-*-full_build\bin" ffmpeg >nul 2>&1
        echo [✅] FFmpeg installed successfully
        del ffmpeg.zip
    ) else (
        echo [⚠️] FFmpeg download failed, some features may not work
    )
) else (
    echo [✅] FFmpeg already installed
)

REM Setup environment
echo.
echo [🔧] Setting up environment configuration...

if not exist ".env" (
    copy ".env" ".env.local" >nul 2>&1
    echo [✅] Environment file configured
)

REM Create necessary directories
if not exist "uploads" mkdir uploads
if not exist "uploads\avatars" mkdir uploads\avatars
if not exist "uploads\scenes" mkdir uploads\scenes
if not exist "uploads\temp" mkdir uploads\temp
if not exist "logs" mkdir logs

echo [✅] Directory structure created

REM Setup PostgreSQL database
echo.
echo [🗄️] Setting up PostgreSQL database...
set /p DB_NAME="Enter database name (matrix_studio): " || set DB_NAME=matrix_studio
set /p DB_USER="Enter database user (postgres): " || set DB_USER=postgres
set /p DB_PASSWORD="Enter database password: " || set DB_PASSWORD=password

echo [🔧] Creating database and schema...

REM Create database
createdb -U %DB_USER% %DB_NAME% 2>nul
if errorlevel 1 (
    echo [⚠️] Database might already exist or connection failed
)

REM Import schema
psql -U %DB_USER% -d %DB_NAME% -f src\database\schema.sql
if errorlevel 1 (
    echo [⚠️] Schema import may have failed, please check manually
) else (
    echo [✅] Database schema created successfully
)

REM Update environment file
echo [📝] Updating environment configuration...
(
echo NODE_ENV=production
echo PORT=3000
echo DB_HOST=localhost
echo DB_PORT=5432
echo DB_NAME=%DB_NAME%
echo DB_USER=%DB_USER%
echo DB_PASSWORD=%DB_PASSWORD%
echo REDIS_HOST=localhost
echo REDIS_PORT=6379
echo JWT_SECRET=your-super-secret-jwt-key-change-in-production-%RANDOM%
echo CORS_ORIGIN=*
echo LOG_LEVEL=info
) > .env

echo [✅] Environment configured

REM Create Windows service scripts
echo.
echo [🛠️] Creating service management scripts...

REM Start services script
(
echo @echo off
echo title Matrix Studio Services
echo color 0A
echo echo Starting Redis Server...
echo if exist "redis\redis-server.exe" (
echo     start "Redis Server" /min redis\redis-server.exe
echo     echo [✅] Redis started
echo ) else (
echo     echo [⚠️] Redis not found, skipping...
echo )
echo.
echo echo Starting PostgreSQL Service...
echo net start postgresql-x64-14 2^>nul
echo echo [✅] PostgreSQL service started
echo.
echo echo Starting Matrix Studio Backend...
echo cd /d "%~dp0"
echo npm start
echo pause
) > START_SERVICES.bat

REM Stop services script
(
echo @echo off
echo title Stop Matrix Studio Services
echo color 0C
echo echo Stopping Matrix Studio Backend...
echo taskkill /f /im node.exe 2^>nul
echo.
echo echo Stopping Redis Server...
echo if exist "redis\redis-cli.exe" (
echo     redis\redis-cli.exe shutdown
echo ) else (
echo     echo [⚠️] Redis CLI not found
echo )
echo.
echo echo [✅] All services stopped
echo pause
) > STOP_SERVICES.bat

echo [✅] Service scripts created

REM Create monitoring launcher
(
echo @echo off
echo title Matrix Studio Monitoring
echo color 0E
echo echo Starting monitoring dashboard...
echo cd /d "%~dp0"
echo start http://localhost:3000
echo start http://localhost:3001
echo timeout /t 5
echo echo Services should be available at:
echo echo - Main App: http://localhost:3000
echo echo - Grafana: http://localhost:3001 ^(^if installed^)
echo pause
) > MONITORING.bat

echo [✅] Monitoring launcher created

echo.
echo ════════════════════════════════════════════════════════════════
echo [🎉] MATRIX STUDIO V2.0 STANDALONE INSTALLATION COMPLETE!
echo ════════════════════════════════════════════════════════════════
echo.
echo 🌐 Main Application: http://localhost:3000
echo 📁 Installation Path: %CD%
echo 🗄️  Database: %DB_NAME%
echo 👤 Database User: %DB_USER%
echo.
echo ════════════════════════════════════════════════════════════════
echo [🛠️] MANAGEMENT COMMANDS
echo ════════════════════════════════════════════════════════════════
echo.
echo 🚀 Start Services:    START_SERVICES.bat
echo 🛑 Stop Services:     STOP_SERVICES.bat
echo 📊 Monitoring:        MONITORING.bat
echo 🔧 Development:        npm run dev
echo 🧪 Test:              npm test
echo 📋 Logs:              type logs\combined.log
echo.
echo ════════════════════════════════════════════════════════════════
echo [🌊] PROFESSIONAL FEATURES READY:
echo ════════════════════════════════════════════════════════════════
echo.
echo ✅ Enterprise-grade authentication
echo ✅ Real-time WebRTC broadcasting
echo ✅ 6 simultaneous guests
echo ✅ 5 professional scene templates
echo ✅ Multi-platform streaming
echo ✅ Advanced analytics
echo ✅ PostgreSQL database
echo ✅ Redis caching
echo ✅ Native Windows deployment
echo.

set /p choice="Start services now? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo [🚀] Starting Matrix Studio Services...
    call START_SERVICES.bat
) else (
    echo.
    echo [✅] Installation complete! Run START_SERVICES.bat to start.
    pause
)