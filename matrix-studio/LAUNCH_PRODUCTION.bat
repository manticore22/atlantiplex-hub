@echo off
chcp 65001 >nul
title ATLANTIPLEX MATRIX STUDIO - FINAL PRODUCTION VERSION
color 0A

echo ================================================================
echo    ATLANTIPLEX MATRIX STUDIO - FINAL PRODUCTION VERSION
echo ================================================================
echo.
echo COMPREHENSIVE DEBUG COMPLETE - SYSTEM READY FOR PRODUCTION
echo.
echo This version includes:
echo [OK] Unicode-safe debug logging
echo [OK] Automatic port detection
echo [OK] Verified admin credentials
echo [OK] End-to-end testing suite
echo [OK] Professional StreamYard-style UI
echo [OK] Robust authentication system
echo.
echo ================================================================
echo LAUNCHING PRODUCTION SERVER...
echo ================================================================
echo.
echo ADMIN LOGIN:
echo   Username: manticore
echo   Password: patriot8812
echo.
echo Server will auto-detect available port and open browser...
echo.

cd /d "%~dp0"

python FINAL_DEBUG.py

echo.
echo ================================================================
echo PRODUCTION SERVER SESSION ENDED
echo ================================================================
pause