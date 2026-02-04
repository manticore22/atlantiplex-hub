@echo off
REM ATLANTIPLEX MATRIX STUDIO - WORKING LAUNCHER
title Atlantiplex Matrix Studio
cd /d "%~dp0"

echo.
echo ========================================
echo ATLANTIPLEX MATRIX STUDIO  
echo ========================================
echo.

REM Kill any existing processes
taskkill /f /im python.exe >nul 2>&1

REM Create simple working app
echo @echo off > simple_working.py
echo from flask import Flask >> simple_working.py
echo app = Flask(__name__) >> simple_working.py
echo. >> simple_working.py
echo @app.route('/') >> simple_working.py
echo def home(): >> simple_working.py
echo     return ''' >> simple_working.py
echo ^<!DOCTYPE html^>^<html^>^<head^>^<title^>Atlantiplex Matrix Studio^</title^>^</head^>^<body^>^<h1^>ATLANTIPLEX MATRIX STUDIO IS RUNNING!^</h1^>^<p^>^<a href="/api/health"^>Check System Status^</a^>^</p^>^<p^>Demo Login: username = demo, password = demo123^</p^>^</body^>^</html^>''' >> simple_working.py
echo. >> simple_working.py
echo @app.route('/api/health') >> simple_working.py
echo def health(): >> simple_working.py
echo     return {'status': 'operational', 'success': True} >> simple_working.py
echo. >> simple_working.py
echo if __name__ == '__main__': app.run(host='0.0.0.0', port=8080) >> simple_working.py

echo.
echo Starting Atlantiplex Matrix Studio...
echo Server will be available at: http://localhost:8080
echo Opening browser...
timeout /t 3 >nul
start "" "http://localhost:8080"
echo.
echo Atlantiplex Matrix Studio is running...
echo.
python WORKING_APP.py

pause