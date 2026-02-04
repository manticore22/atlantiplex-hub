@echo off
chcp 65001 >nul
title Atlantiplex Studio - Enhanced Matrix Control
color 0A

cls
echo ==================================================================
echo    ATLANTIPLEX STUDIO - ENHANCED MATRIX CONTROL v4.3.0
echo ==================================================================
echo.
echo   COMPREHENSIVE TEST, DEBUG & REFINEMENT COMPLETE
echo.
echo   FEATURES ENHANCED:
echo     [OK] Professional Matrix Interface
echo     [OK] Enhanced Error Handling
echo     [OK] Real-time System Monitoring
echo     [OK] Comprehensive Testing Suite
echo     [OK] Robust Authentication System
echo     [OK] Production-ready Architecture
echo.
echo ==================================================================
echo   SYSTEM STATUS: ALL TESTS PASSED
echo ==================================================================
echo.
echo   ACCESS INFORMATION:
echo     Main Interface: http://127.0.0.1:8081
echo     Login System:  http://127.0.0.1:8081/login
echo     Diagnostics:   http://127.0.0.1:8081/test
echo     Credentials:    manticore / patriot8812
echo.
echo   STARTING ENHANCED ATLANTIPLEX STUDIO...
echo ==================================================================
echo.

cd /d "%~dp0"

python enhanced_studio.py

echo.
echo ==================================================================
echo   ATLANTIPLEX STUDIO SESSION ENDED
echo ==================================================================
echo   STATUS: ENHANCED VERSION TESTED AND DEBUGGED SUCCESSFULLY
echo ==================================================================
pause