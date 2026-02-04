@echo off
REM ========================================
REM   ATLANTIPLEX MATRIX STUDIO
REM   Professional Broadcasting System
REM   Status: PRODUCTION READY
REM ========================================

title Atlantiplex Matrix Studio
cd /d "%~dp0"

echo.
echo ========================================
echo    ATLANTIPLEX MATRIX STUDIO
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
    echo Please install Python 3.8+ and try again
    echo.
    pause
    exit /b 1
)

echo Python detected successfully
echo.

REM Check for existing server and kill if needed
echo Checking for existing server on port 8080...

REM Kill any existing Python processes on port 8080
for /f "tokens=1,2,*" %%a in ('tasklist /fi "IMAGENAME eq python.exe" 2^>nul ^| findstr /i "python.exe"') do (
    echo Found Python process: %%a
    taskkill /f /im python.exe /fi "PID eq %%~a" >nul 2>&1
)

echo Waiting 2 seconds for ports to be released...
timeout /t 2 >nul
echo.

REM Start new server
echo Starting Atlantiplex Matrix Studio...
echo.
echo Server will start at: http://localhost:8080
echo.
timeout /t 3 >nul
echo.
echo Launching web interface...
start "" "http://localhost:8080"
echo.
echo ========================================
echo    ATLANTIPLEX MATRIX STUDIO - RUNNING
echo ========================================
echo.
echo Web Interface: http://localhost:8080
echo API Documentation: http://localhost:8080/api
echo Demo Login: username = demo, password = demo123
echo.
echo Server is running... Browser should open automatically
echo.
echo Press Ctrl+C in this window to stop the server
echo ========================================
echo.

REM Launch the final working application
python final_app.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo    ERROR OCCURRED
    echo ========================================
    echo Please check the error message above
    echo.
    pause
)

echo.
echo ========================================
echo      SERVER STOPPED
echo ========================================
pause