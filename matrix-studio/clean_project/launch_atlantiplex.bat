@echo off
chcp 65001 >nul
title Atlantiplex Studio - Lightning in a Bottle
color 0B

echo ================================================================
echo    ATLANTIPLEX STUDIO - CYBERPUNK EDITION
echo ================================================================
echo.
echo MAX HEADROOM INTERFACE - CYBERPUNK STYLE
echo.
echo Features:
echo   - Cyberpunk terminal interface
echo   - Max Headroom visual effects  
echo   - Green terminal aesthetic
echo   - Real guest invitation system
echo   - Admin authentication
echo   - End-to-end testing suite
echo.
echo ================================================================
echo INITIATING ATLANTIPLEX STUDIO...
echo ================================================================
echo.
echo ADMIN ACCESS:
echo    Username: manticore
echo    Password: patriot8812
echo.
echo Studio will auto-detect available port and open browser...
echo ================================================================

cd /d "%~dp0"

python atlantiplex_studio.py

echo.
echo ================================================================
echo ATLANTIPLEX STUDIO SESSION ENDED
echo ================================================================
pause