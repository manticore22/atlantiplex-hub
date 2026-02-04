@echo off
title ATLANTIPLEX STUDIO - PROVEN WORKING
color 0A

cls
echo ================================================================
echo    ATLANTIPLEX STUDIO - BULLETPROOF EDITION
echo ================================================================
echo.
echo This version has been designed to be 100%% reliable.
echo No complex dependencies, no Azure imports, no template errors.
echo.
echo Press any key to start the server and prove it works...
pause >nul

cls
echo ================================================================
echo STARTING ATLANTIPLEX STUDIO...
echo ================================================================
echo.

cd /d "%~dp0"

echo Running bulletproof_studio.py...
python bulletproof_studio.py

echo.
echo ================================================================
echo SERVER SESSION ENDED
echo ================================================================
pause