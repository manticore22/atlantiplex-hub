@echo off
title Atlantiplex Studio
color 0B

echo ================================================================
echo    ATLANTIPLEX STUDIO - LIGHTNING IN A BOTTLE
echo ================================================================
echo.
echo Lightning-fast broadcasting platform
echo.
echo Admin Credentials:
echo    Username: manticore
echo    Password: patriot8812
echo.
echo Starting studio...
echo ================================================================

cd /d "%~dp0"

python FINAL_DEBUG.py

echo.
echo Studio session ended.
pause