@echo off
title 🌊 MATRIX BROADCAST STUDIO - RELIABLE LAUNCHER
color 0B
echo.
echo ========================================
echo    🌊 MATRIX BROADCAST STUDIO
echo        RELIABLE LAUNCHER v1.0
echo ========================================
echo.

REM Set working directory
set "MATRIX_DIR=%~dp0matrix-studio"
set "LOG_FILE=%~dp0matrix_startup.log"

echo [INFO] Checking Matrix Studio directory...
if not exist "%MATRIX_DIR%" (
    echo [ERROR] Matrix Studio directory not found!
    echo [INFO] Creating directory structure...
    mkdir "%MATRIX_DIR%" 2>nul
    echo [SUCCESS] Directory created
)

echo [INFO] Changing to Matrix Studio directory...
cd /d "%MATRIX_DIR%"

echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python first.
    pause
    exit /b 1
)

echo [INFO] Starting Matrix Broadcast Studio...
echo [INFO] Log file: %LOG_FILE%
echo [INFO] Web Interface: http://localhost:8080
echo [INFO] Press Ctrl+C to stop the server
echo.

REM Start with logging
echo [%DATE% %TIME%] Starting Matrix Broadcast Studio... >> "%LOG_FILE%"
python production_ready_backend.py --port 8080 2>&1 | tee -a "%LOG_FILE%"

echo.
echo [INFO] Matrix Broadcast Studio stopped
pause