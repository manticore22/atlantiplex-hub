@echo off
REM Atlantiplex Matrix Studio - Clean Working Launcher
cd /d "%~dp0"

echo.
echo Starting Atlantiplex Matrix Studio...
echo.

python SIMPLIFIED_WORKING.py

echo.
echo.
echo ========================================
echo    Atlantiplex Matrix Studio
echo ========================================
echo Server will be available at: http://localhost:8081
echo Health Check: http://localhost:8081/api/health
echo API Documentation: http://localhost:8081/api
echo Demo Login: username = demo, password = demo123
echo.
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

pause