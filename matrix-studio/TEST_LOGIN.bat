@echo off
echo Testing Atlantiplex Matrix Studio Login
echo.
echo Admin Credentials:
echo   Username: manticore
echo   Password: patriot8812
echo.
echo Launching server...
cd /d "%~dp0"
start "" "http://localhost:8081"
python MATRIX_STUDIO_PRO.py
pause