@echo off
chcp 65001 >nul
title Atlantiplex Studio - Cyberpunk Edition
color 0A

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
echo   - Professional broadcasting controls
echo.
echo ================================================================
echo INITIATING CYBERPUNK SYSTEM...
echo ================================================================
echo.
echo ADMIN ACCESS:
echo    Username: manticore
echo    Password: patriot8812
echo.
echo Terminal initializing... [SCAN COMPLETE]
echo Matrix grid online... [READY]
echo Cyberpunk interface loading...
echo ================================================================

cd /d "%~dp0"
find . -name "atlantiplex_studio.py" -type f
if exist %%f (
    echo Found atlantiplex_studio.py at: %%f
    python "%%f"
) else (
    echo ERROR: atlantiplex_studio.py not found!
    echo Please check project directory.
)
echo.
echo ================================================================
echo CYBERPUNK STUDIO SESSION ENDED
echo ================================================================
pause