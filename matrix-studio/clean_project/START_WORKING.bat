@echo off
title Atlantiplex Studio - WORKING VERSION
color 0B

echo ================================================================
echo    ATLANTIPLEX STUDIO - MINIMAL WORKING VERSION
echo ================================================================
echo.
echo ✅ SOLVED: Connection Issues Fixed
echo ✅ READY: Immediate Access
echo ✅ SIMPLE: No Complex Dependencies
echo.
echo SERVER URL: http://127.0.0.1:8080
echo LOGIN: manticore / patriot8812
echo.
echo ================================================================
echo STARTING ATLANTIPLEX STUDIO...
echo ================================================================

cd /d "%~dp0"

python minimal_studio.py

echo.
echo ================================================================
echo ATLANTIPLEX STUDIO SESSION ENDED
echo ================================================================
pause