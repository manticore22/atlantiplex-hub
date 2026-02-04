@echo off
chcp 65001 >nul
title ATLANTIPLEX MATRIX STUDIO - FINAL PRODUCTION LAUNCHER
color 0A
echo.
echo ================================================================
echo    ATLANTIPLEX MATRIX STUDIO - FINAL PRODUCTION LAUNCHER
echo ================================================================
echo.
echo Starting Atlantiplex Matrix Studio...
echo This will launch the complete broadcast studio system.
echo.
echo Access Points:
echo   - Main Studio: http://localhost:8081
echo   - API Documentation: http://localhost:8081/api
echo   - Health Check: http://localhost:8081/api/health
echo.
echo Demo Login Credentials:
echo   - Username: demo
echo   - Password: demo123
echo.
echo Press Ctrl+C to stop the server at any time.
echo ================================================================
echo.

cd /d "%~dp0"

echo Starting server...
echo Browser will open automatically at http://localhost:8081
timeout /t 2 >nul
start "" "http://localhost:8081"

python COMPLETE_WORKING.py

echo.
echo Server stopped. Press any key to exit...
pause >nul