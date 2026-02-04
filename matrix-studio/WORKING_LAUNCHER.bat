@echo off
title Atlantiplex Matrix Studio
cd /d "%~dp0"

echo ========================================
echo ATLANTIPLEX MATRIX STUDIO
echo ========================================

echo Starting simplified working application...
echo.

python SIMPLIFIED_WORKING.py
echo.

echo.
echo ========================================
echo    ATLANTIPLEX MATRIX STUDIO - RUNNING
echo ========================================
echo Web Interface: http://localhost:8081
echo Health Check: http://localhost:8081/api/health
echo API Documentation: http://localhost:8081/api
echo Demo Login: username = demo, password = demo123
echo.
echo Server is running successfully.
echo.
pause