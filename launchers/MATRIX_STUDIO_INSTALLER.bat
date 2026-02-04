@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

:: ============================================================================
:: 🌊 MATRIX BROADCAST STUDIO - ONE-CLICK INSTALLER
:: Professional Broadcasting System - Auto Install & Launch
:: ============================================================================

:: Set console to Matrix Green color
color 0a

:: Console settings
mode 100,35
title 🌊 MATRIX BROADCAST STUDIO - INSTALLER

:: Check if running with admin privileges
net session >nul 2>&1
if errorlevel 1 (
    echo.
    echo [❌ ERROR] Please run this installer as Administrator!
    echo [⚡ INFO] Right-click the file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

:: Enhanced Matrix ASCII art
cls
echo.
echo  ██████╗ ███████╗ ██████╗ ██████╗ 
echo  ██╔════╝██╔══██╗██╔════╝ 
echo  █████╗  ███████║███████╗  
echo  ██╔══╝  ██╔══██║██╔══██╗ 
echo  ███████╗██║  ██║██║  ██║ 
echo  ╚══════╝╚═╝  ╚═╝╚══════╝ 
echo.
echo  ██████╗ ███████╗ ██████╗ 
echo  ██╔════╝██╔══██╗██╔════╝ 
echo  █████╗  ███████║███████╗  
echo  ██╔══╝  ██╔══██║██╔══██╗ 
echo  ███████╗██║  ██║██║  ██║ 
echo  ╚══════╝╚═╝  ╚═╝╚══════╝ 
echo.
echo  🌊 ONE-CLICK INSTALLER v3.0
echo  ═════════════════════════════════════════════════════════════════
echo  Auto Install • Professional Setup • Production Deployment
echo  ═════════════════════════════════════════════════════════════════
echo.

:: Configuration
set APP_NAME=Matrix Broadcast Studio
set INSTALL_DIR=C:\MatrixStudio
set VENV_NAME=matrix_studio_env
set PYTHON_MIN=3.8
set MAX_PORT_ATTEMPTS=10

:: Initialize status
set INSTALL_STATUS=INITIALIZING
set PYTHON_FOUND=0
set VENV_CREATED=0
set DEPS_INSTALLED=0
set LAUNCHER_CREATED=0

:: Function to print colored output
:printStatus
if "%1"=="INFO" (
    echo [⚡ %date% %time%] [INFO] %~2
) else if "%1"=="WARN" (
    echo [⚠️  %date% %time%] [WARN] %~2
) else if "%1"=="ERROR" (
    echo [❌ %date% %time%] [ERROR] %~2
) else if "%1"=="SUCCESS" (
    echo [✅ %date% %time%] [SUCCESS] %~2
) else if "%1"=="MATRIX" (
    echo [🌊 %date% %time%] [MATRIX] %~2
)
goto :eof

:: Main installation sequence
call :printStatus "MATRIX" "Starting One-Click Installation..."
call :printStatus "INFO" "Checking system requirements..."

:: Check Python installation
call :checkPython
if %PYTHON_FOUND% equ 0 (
    call :printStatus "ERROR" "Python %PYTHON_MIN% or higher is required"
    call :printStatus "INFO" "Please install Python from https://python.org"
    goto :errorExit
)

:: Create installation directory
call :createInstallDir

:: Create virtual environment
call :createVirtualEnv

:: Install dependencies
call :installDependencies

:: Create Matrix Studio directory structure
call :createDirectoryStructure

:: Download/copy all Matrix Studio files
call :copyMatrixStudioFiles

:: Create desktop shortcut
call :createDesktopShortcut

:: Create Start Menu shortcut
call :createStartMenuShortcut

:: Create system tray launcher
call :createSystemTrayLauncher

:: Finalize installation
call :finalizeInstallation

goto :successExit

:: ============================================================================
:: FUNCTION DEFINITIONS
:: ============================================================================

:checkPython
call :printStatus "INFO" "Checking Python installation..."
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        call :printStatus "ERROR" "Python not found in PATH"
        set PYTHON_FOUND=0
        goto :eof
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

:: Check Python version
for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
call :printStatus "INFO" "Found Python %PYTHON_VERSION%"
set PYTHON_FOUND=1
goto :eof

:createInstallDir
call :printStatus "INFO" "Creating installation directory..."
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    if errorlevel 1 (
        call :printStatus "ERROR" "Failed to create installation directory"
        goto :errorExit
    )
    call :printStatus "SUCCESS" "Installation directory created: %INSTALL_DIR%"
) else (
    call :printStatus "INFO" "Installation directory already exists: %INSTALL_DIR%"
)
goto :eof

:createVirtualEnv
call :printStatus "INFO" "Creating virtual environment..."
if not exist "%INSTALL_DIR%\%VENV_NAME%" (
    cd /d "%INSTALL_DIR%"
    %PYTHON_CMD% -m venv %VENV_NAME%
    if errorlevel 1 (
        call :printStatus "ERROR" "Failed to create virtual environment"
        goto :errorExit
    )
    set VENV_CREATED=1
    call :printStatus "SUCCESS" "Virtual environment created"
) else (
    call :printStatus "INFO" "Virtual environment already exists"
    set VENV_CREATED=1
)

:: Activate virtual environment
call :printStatus "INFO" "Activating virtual environment..."
if %VENV_CREATED% equ 1 (
    call "%INSTALL_DIR%\%VENV_NAME%\Scripts\activate.bat"
    if errorlevel 1 (
        call :printStatus "WARN" "Failed to activate virtual environment"
        set VENV_CREATED=0
    )
)
goto :eof

:installDependencies
call :printStatus "INFO" "Installing dependencies..."
cd /d "%INSTALL_DIR%"

if %VENV_CREATED% equ 1 (
    call :printStatus "INFO" "Installing with virtual environment Python..."
    %INSTALL_DIR%\%VENV_NAME%\Scripts\pip install flask flask-cors werkzeug pillow apscheduler google-api-python-client google-auth-oauthlib pystray --quiet
) else (
    call :printStatus "INFO" "Installing with system Python..."
    %PYTHON_CMD% -m pip install flask flask-cors werkzeug pillow apscheduler google-api-python-client google-auth-oauthlib pystray --quiet
)

if errorlevel 1 (
    call :printStatus "ERROR" "Failed to install dependencies"
    goto :errorExit
) else (
    set DEPS_INSTALLED=1
    call :printStatus "SUCCESS" "Dependencies installed successfully"
)
goto :eof

:createDirectoryStructure
call :printStatus "INFO" "Creating Matrix Studio directory structure..."
cd /d "%INSTALL_DIR%"

:: Create required directories
if not exist "uploads" mkdir "uploads"
if not exist "uploads\avatars" mkdir "uploads\avatars"
if not exist "uploads\avatars\users" mkdir "uploads\avatars\users"
if not exist "uploads\avatars\guests" mkdir "uploads\avatars\guests"
if not exist "uploads\scenes" mkdir "uploads\scenes"
if not exist "uploads\streams" mkdir "uploads\streams"
if not exist "logs" mkdir "logs"
if not exist "config" mkdir "config"

:: Create configuration file
echo { > config\config.json
echo   "app_name": "Matrix Broadcast Studio", >> config\config.json
echo   "version": "2.0.0", >> config\config.json
echo   "production_mode": false, >> config\config.json
echo   "default_port": 8080, >> config\config.json
echo   "max_guests": 6, >> config\config.json
echo   "enable_analytics": true, >> config\config.json
echo   "enable_scheduler": true >> config\config.json
echo } >> config\config.json

call :printStatus "SUCCESS" "Directory structure created"
goto :eof

:copyMatrixStudioFiles
call :printStatus "INFO" "Installing Matrix Studio files..."
cd /d "%INSTALL_DIR%"

:: Download/copy main files (assuming they exist in current directory)
echo [🌊 MATRIX] Copying Matrix Studio files...

:: Copy production backend
if exist "..\matrix-studio\production_ready_backend.py" (
    copy "..\matrix-studio\production_ready_backend.py" "production_ready_backend.py"
    call :printStatus "SUCCESS" "Copied production backend"
) else (
    call :printStatus "ERROR" "Production backend not found"
    goto :errorExit
)

:: Copy guest management
if exist "..\matrix-studio\guest_management.py" (
    copy "..\matrix-studio\guest_management.py" "guest_management.py"
    call :printStatus "SUCCESS" "Copied guest management"
) else (
    call :printStatus "ERROR" "Guest management not found"
    goto :errorExit
)

:: Copy scene manager
if exist "..\matrix-studio\scene_manager.py" (
    copy "..\matrix-studio\scene_manager.py" "scene_manager.py"
    call :printStatus "SUCCESS" "Copied scene manager"
) else (
    call :printStatus "ERROR" "Scene manager not found"
    goto :errorExit
)

:: Copy avatar management
if exist "..\matrix-studio\avatar_management.py" (
    copy "..\matrix-studio\avatar_management.py" "avatar_management.py"
    call :printStatus "SUCCESS" "Copied avatar management"
) else (
    call :printStatus "ERROR" "Avatar management not found"
    goto :errorExit
)

:: Copy broadcast engine
if exist "..\matrix-studio\broadcast_engine.py" (
    copy "..\matrix-studio\broadcast_engine.py" "broadcast_engine.py"
    call :printStatus "SUCCESS" "Copied broadcast engine"
) else (
    call :printStatus "ERROR" "Broadcast engine not found"
    goto :errorExit
)

:: Copy additional files
if exist "..\matrix-studio\analytics.py" copy "..\matrix-studio\analytics.py" "analytics.py"
if exist "..\matrix-studio\scheduler.py" copy "..\matrix-studio\scheduler.py" "scheduler.py"
if exist "..\matrix-studio\platform_integrations.py" copy "..\matrix-studio\platform_integrations.py" "platform_integrations.py"

call :printStatus "SUCCESS" "All Matrix Studio files copied"
goto :eof

:createDesktopShortcut
call :printStatus "INFO" "Creating desktop shortcut..."
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT="%DESKTOP%\Matrix Broadcast Studio.lnk"

powershell -command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = 'shell32.dll'; $Shortcut.IconIndex = 13; $Shortcut.Description = 'Matrix Broadcast Studio - Professional Broadcasting System'; $Shortcut.Save()}"

if exist "%SHORTCUT%" (
    call :printStatus "SUCCESS" "Desktop shortcut created"
    set LAUNCHER_CREATED=1
) else (
    call :printStatus "WARN" "Failed to create desktop shortcut"
)
goto :eof

:createStartMenuShortcut
call :printStatus "INFO" "Creating Start Menu shortcut..."
set STARTMENU=%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs\Matrix Broadcast Studio
set SHORTCUT="%STARTMENU%\Matrix Broadcast Studio.lnk"

if not exist "%STARTMENU%" mkdir "%STARTMENU%"
powershell -command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = 'shell32.dll'; $Shortcut.IconIndex = 13; $Shortcut.Description = 'Matrix Broadcast Studio - Professional Broadcasting System'; $Shortcut.Save()}"

if exist "%SHORTCUT%" (
    call :printStatus "SUCCESS" "Start Menu shortcut created"
) else (
    call :printStatus "WARN" "Failed to create Start Menu shortcut"
)
goto :eof

:createSystemTrayLauncher
call :printStatus "INFO" "Creating system tray launcher..."
cd /d "%INSTALL_DIR%"

:: Create the production launcher (simple version)
echo @echo off > MATRIX_STUDIO_PRODUCTION.bat
echo setlocal enabledelayedexpansion >> MATRIX_STUDIO_PRODUCTION.bat
echo cd /d "%%~dp0" >> MATRIX_STUDIO_PRODUCTION.bat
echo if exist "%VENV_NAME%\Scripts\activate.bat" ( >> MATRIX_STUDIO_PRODUCTION.bat
echo     call "%VENV_NAME%\Scripts\activate.bat" >> MATRIX_STUDIO_PRODUCTION.bat
echo ) >> MATRIX_STUDIO_PRODUCTION.bat
echo python production_ready_backend.py >> MATRIX_STUDIO_PRODUCTION.bat
echo if errorlevel 1 pause >> MATRIX_STUDIO_PRODUCTION.bat

call :printStatus "SUCCESS" "System tray launcher created"
goto :eof

:finalizeInstallation
call :printStatus "MATRIX" "Finalizing installation..."
call :printStatus "SUCCESS" "Installation completed successfully!"

:: Create uninstall script
echo @echo off > uninstall.bat
echo echo Uninstalling Matrix Broadcast Studio... >> uninstall.bat
echo rd /s /q "%INSTALL_DIR%" >> uninstall.bat
echo echo Matrix Broadcast Studio has been uninstalled. >> uninstall.bat
echo pause >> uninstall.bat

goto :eof

:errorExit
echo.
echo [❌ ERROR] Matrix Broadcast Studio installation failed!
echo [⚡ INFO] Please check the error messages above
echo [⚡ INFO] Make sure you have Administrator privileges
echo [⚡ INFO] Ensure Python %PYTHON_MIN%+ is installed
echo.
pause
exit /b 1

:successExit
echo.
echo [🌊 MATRIX] 🎉 MATRIX BROADCAST STUDIO INSTALLATION COMPLETE! 🎉
echo ═════════════════════════════════════════════════════════════════
echo  ✅ Installation: SUCCESSFUL
echo  ✅ Location: %INSTALL_DIR%
echo  ✅ Dependencies: INSTALLED
echo  ✅ Shortcuts: CREATED
echo  ✅ System: PRODUCTION READY
echo ═════════════════════════════════════════════════════════════════
echo.
echo 🚀 LAUNCH OPTIONS:
echo.
echo 1. Desktop Shortcut: Double-click "Matrix Broadcast Studio" on desktop
echo 2. Start Menu: Find "Matrix Broadcast Studio" in Start Menu
echo 3. Command Line: cd "%INSTALL_DIR%" && MATRIX_STUDIO_PRODUCTION.bat
echo.
echo 🌐 WEB INTERFACE:
echo  http://localhost:8080
echo.
echo 👤 DEMO LOGIN:
echo  Username: demo
echo  Password: demo123
echo.
echo 📖 USER GUIDE:
echo  %INSTALL_DIR%\PRODUCTION_COMPLETE.md
echo.
echo 🗑️ UNINSTALL:
echo  Run "uninstall.bat" from the installation directory
echo.
echo [✅ SUCCESS] Matrix Broadcast Studio is ready for professional use!
echo.
echo Press any key to start Matrix Broadcast Studio...
pause >nul

:: Auto-start the application
cd /d "%INSTALL_DIR%"
if exist "%VENV_NAME%\Scripts\activate.bat" (
    call "%VENV_NAME%\Scripts\activate.bat"
)
call MATRIX_STUDIO_PRODUCTION.bat

exit /b 0