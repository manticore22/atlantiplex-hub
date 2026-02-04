@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

:: ============================================================================
:: 🌊 MATRIX BROADCAST STUDIO - SYSTEM TRAY LAUNCHER
:: Background operation with system tray integration
:: ============================================================================

:: Set console to Matrix Green color
color 0a

:: Console settings
mode 80,25
title 🌊 MATRIX BROADCAST STUDIO - SYSTEM TRAY

:: Matrix ASCII art
cls
echo.
echo  ███████╗████████╗██████╗ ███████╗███████╗██████╗ 
echo  ██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔════╝██╔══██╗
echo  █████╗     ██║   ██████╔╝█████╗  █████╗  ██████╔╝
echo  ██╔══╝     ██║   ██╔══██╗██╔══╝  ██╔══╝  ██╔══██╗
echo  ██║        ██║   ██║  ██║███████╗███████╗██║  ██║
echo  ╚═╝        ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝
echo.
echo  ██████╗ ███████╗ █████╗ ██████╗ 
echo  ██╔══██╗██╔════╝██╔══██╗██╔══██╗
echo  ██║  ██║█████╗  ███████║██║  ██║
echo  ██║  ██║██╔══╝  ██╔══██║██║  ██║
echo  ██████╔╝███████╗██║  ██║██████╔╝
echo  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═════╝ 
echo.
echo  🌊 SYSTEM TRAY MODE
echo  ═════════════════════════════════════════════════════════════════════
echo  Background Operation • Quick Access • System Tray Integration
echo  ═════════════════════════════════════════════════════════════════════
echo.

:: Configuration
set PORT=8080
set PYTHON_CMD=python

:: Function to check dependencies
:checkDependencies
echo [⚡ INFO] Checking system dependencies...

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo [❌ ERROR] Python not found
        goto :errorExit
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

:: Check required files
if not exist "matrix_studio_tray.py" (
    echo [❌ ERROR] System tray script not found
    goto :errorExit
)

if not exist "matrix_studio_final.py" (
    echo [❌ ERROR] Main application script not found
    goto :errorExit
)

:: Check optional system tray dependencies
echo [⚡ INFO] Checking for system tray dependencies...
%PYTHON_CMD% -c "import pystray" >nul 2>&1
if errorlevel 1 (
    echo [⚠️  WARNING] System tray libraries not found
    echo [⚡ INFO] Installing system tray dependencies...
    %PYTHON_CMD% -m pip install pystray pillow --quiet
    if errorlevel 1 (
        echo [⚠️  WARNING] Failed to install system tray dependencies
        echo [⚡ INFO] Running in console mode instead...
        set NO_TRAY=1
    ) else (
        echo [✅ SUCCESS] System tray dependencies installed
        set NO_TRAY=0
    )
) else (
    echo [✅ SUCCESS] System tray dependencies available
    set NO_TRAY=0
)

goto :startTray

:startTray
echo.
echo [🌊 MATRIX] Starting Matrix Broadcast Studio in System Tray mode...

:: Find available port
netstat -an | findstr ":%PORT%" >nul 2>&1
if not errorlevel 1 (
    echo [⚠️  WARNING] Port %PORT% is in use
    set /p PORT="Enter alternative port (default 8081): "
    if "!PORT!"=="" set PORT=8081
)

:: Start the tray application
if %NO_TRAY% equ 1 (
    echo [⚡ INFO] Starting without system tray...
    %PYTHON_CMD% matrix_studio_tray.py --port %PORT% --no-tray
) else (
    echo [⚡ INFO] Starting with system tray integration...
    echo [📍 Look for the Matrix icon in your system tray
    echo [📍 Right-click the icon for options
    echo.
    %PYTHON_CMD% matrix_studio_tray.py --port %PORT%
)

if errorlevel 1 (
    goto :errorExit
) else (
    goto :successExit
)

:errorExit
echo.
echo [❌ ERROR] Failed to start Matrix Broadcast Studio
echo [⚡ INFO] Please check the error messages above
pause
exit /b 1

:successExit
echo.
echo [✅ SUCCESS] Matrix Broadcast Studio stopped
exit /b 0