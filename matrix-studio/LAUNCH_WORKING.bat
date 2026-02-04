@echo off
chcp 65001 >nul
title Atlantiplex Studio - Lightning in a Bottle
color 0B

echo ================================================================
echo    ATLANTIPLEX STUDIO - LIGHTNING IN A BOTTLE
echo ================================================================
echo.
echo [LIGHTNING] Lightning-fast broadcasting platform
echo.
echo This version includes:
echo [OK] Professional lightning branding
echo [OK] StreamYard-style interface
echo [OK] Unicode-safe debug logging
echo [OK] Automatic port detection
echo [OK] Verified admin credentials
echo [OK] End-to-end testing suite
echo.
echo ================================================================
echo LAUNCHING ATLANTIPLEX STUDIO...
echo ================================================================
echo.
echo [AUTH] ADMIN LOGIN:
echo    Username: manticore
echo    Password: patriot8812
echo.
echo Studio will auto-detect available port and open browser...
echo ================================================================

cd /d "%~dp0"

python FINAL_DEBUG.py

echo.
echo ================================================================
echo ATLANTIPLEX STUDIO SESSION ENDED
echo ================================================================
pause