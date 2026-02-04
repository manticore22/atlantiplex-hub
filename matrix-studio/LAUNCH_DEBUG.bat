@echo off
chcp 65001 >nul
title ATLANTIPLEX MATRIX STUDIO - COMPREHENSIVE DEBUG
color 0E

echo ================================================================
echo    ATLANTIPLEX MATRIX STUDIO - COMPREHENSIVE DEBUG VERSION
echo ================================================================
echo.
echo This version includes:
echo - Full debug logging
echo - Auto port detection  
echo - Database verification
echo - End-to-end testing
echo - Detailed error reporting
echo.
echo CREDENTIALS: manticore / patriot8812
echo.
echo Starting debug server...
echo ================================================================

cd /d "%~dp0"

python DEBUG_VERSION.py

echo.
echo ================================================================
echo Server session ended.
echo ================================================================
pause