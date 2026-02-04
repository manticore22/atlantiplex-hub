@echo off
chcp 65001 >nul
title ATLANTIPLEX MATRIX STUDIO - PROFESSIONAL EDITION
color 0A
echo.
echo ================================================================
echo    ATLANTIPLEX MATRIX STUDIO - PROFESSIONAL EDITION
echo ================================================================
echo.
echo Starting Atlantiplex Matrix Studio Professional Edition...
echo.
echo ✨ FEATURES:
echo   - Admin Authentication System
echo   - Gmail OAuth Integration  
echo   - Real Guest Invitation System
echo   - Professional Settings Management
echo   - Modern StreamYard-Style Interface
echo.
echo 🔐 ADMIN LOGIN:
echo   - Username: manticore
echo   - Password: patriot8812
echo.
echo 🌐 Access Points:
echo   - Main Studio: http://localhost:8081
echo   - API Documentation: http://localhost:8081/api
echo   - Health Check: http://localhost:8081/api/health
echo.
echo Press Ctrl+C to stop the server at any time.
echo ================================================================
echo.

cd /d "%~dp0"

echo Starting server and opening browser...
start "" "http://localhost:8081" 2>nul
timeout /t 2 >nul

python MATRIX_STUDIO_PRO.py

echo.
echo Server stopped. Press any key to exit...
pause >nul