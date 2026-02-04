@echo off
REM Atlantiplex Matrix Studio - Working Launcher
cd /d "%~dp0"

echo Starting Atlantiplex Matrix Studio...
echo.

REM Start working application
python SIMPLIFIED_WORKING.py

echo.
echo ========================================
echo    Atlantiplex Matrix Studio
echo ========================================
echo Server will be available at: http://localhost:8081
echo Health Check: http://localhost:8081/api/health
echo API Documentation: http://localhost:8081/api
echo Demo Login: username = demo, password = demo123
echo.
echo Press Ctrl+C to stop
echo.

echo ========================================
echo.
echo.

python SIMPLIFIED_WORKING.py

pause