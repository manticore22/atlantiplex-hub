@echo off
chcp 65001 >nul
title ATLANTIPLEX MATRIX STUDIO - LOGIN TEST
color 0A

echo ================================================================
echo    ATLANTIPLEX MATRIX STUDIO - LOGIN FIX
echo ================================================================
echo.
echo Testing login functionality...
echo.

echo STEP 1: Check database...
cd /d "%~dp0"
if not exist "matrix_studio.db" (
    echo Creating new database...
    python -c "import sqlite3; conn = sqlite3.connect('matrix_studio.db'); cursor = conn.cursor(); cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)'); cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', ('manticore', '5372749be02d62fd17d1d4b377709804e499934f63cab4652b397fd60caede39')); conn.commit(); conn.close(); echo 'Database created successfully'"
) else (
    echo Database exists
)

echo.
echo STEP 2: Verify admin account...
python -c "import sqlite3; conn = sqlite3.connect('matrix_studio.db'); cursor = conn.cursor(); cursor.execute('SELECT username FROM users WHERE username=\"manticore\"'); result = cursor.fetchone(); print('Admin account found:', 'Yes' if result else 'No'); conn.close()"

echo.
echo STEP 3: Test login hash...
python -c "import hashlib; expected = hashlib.sha256('patriot8812'.encode()).hexdigest(); print('Expected hash for patriot8812:', expected)"

echo.
echo STEP 4: Starting web server...
echo.
echo SERVER ACCESS:
echo   - Local: http://127.0.0.1:8083
echo   - Alternative: http://localhost:8083
echo.
echo LOGIN CREDENTIALS:
echo   - Username: manticore
echo   - Password: patriot8812
echo.
echo Opening browser...
timeout /t 2 >nul
start "" "http://127.0.0.1:8083" 2>nul
start "" "http://localhost:8083" 2>nul

python SIMPLE_LOGIN.py

echo.
echo Server stopped.
pause