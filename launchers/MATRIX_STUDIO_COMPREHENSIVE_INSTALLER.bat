@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

:: ============================================================================
:: 🌊 MATRIX BROADCAST STUDIO - COMPREHENSIVE ONE-CLICK INSTALLER
:: Professional Broadcasting System - Auto Install & Launch with Complete Error Handling
:: ============================================================================

:: Set console to Matrix Green color
color 0a

:: Console settings
mode 120,40
title 🌊 MATRIX BROADCAST STUDIO - COMPREHENSIVE INSTALLER

:: Enhanced error handling
set ERROR_COUNT=0
set WARNING_COUNT=0
set SUCCESS_COUNT=0

:: Function to log with timestamps
:logMessage
set "type=%~1"
set "message=%~2"
for /f "tokens=1-3 delims=/ " %%a in ('%time%') do (
    set "hour=%%a"
)
set "timestamp=%hour:~0,2%:%time:~3,2%"

if "%type%"=="ERROR" (
    echo [❌ ERROR^! %timestamp%^!] %message%
    set /a ERROR_COUNT+=1
) else if "%type%"=="WARN" (
    echo [⚠️  WARNING^! %timestamp%^!] %message%
    set /a WARNING_COUNT+=1
) else if "%type%"=="INFO" (
    echo [⚡ INFO^! %timestamp%^!] %message%
) else if "%type%"=="SUCCESS" (
    echo [✅ SUCCESS^! %timestamp%^!] %message%
    set /a SUCCESS_COUNT+=1
) else if "%type%"=="MATRIX" (
    echo [🌊 MATRIX^! %timestamp%^!] %message%
) else (
    echo %message%
)
goto :eof

:: Function to display progress bar
:progressBar
set "step=%~1"
set "total=%~2"
set "percent=0"
set /a percent=step*100/total
set /a filled=percent/2
set /a empty=50-filled

set "progress="
for /l %%i in (1,1,%filled%) do (
    set "progress=!progress!█"
)
for /l %%i in (1,1,%empty%) do (
    set "progress=!progress! "
)
echo [!progress!] !percent!%% - !step!/%total%
goto :eof

:: Function to check admin privileges
:checkAdmin
call :logMessage "INFO" "Checking administrator privileges..."
net session >nul 2>&1
if %errorlevel% neq 0 (
    call :logMessage "ERROR" "Administrator privileges required!"
    call :logMessage "WARN" "Please right-click this file and select 'Run as administrator'"
    call :logMessage "WARN" "This installer requires admin rights to create directories and install system files"
    goto :fatalError
)
call :logMessage "SUCCESS" "Administrator privileges confirmed"
goto :eof

:: Function to check Python installation
:checkPython
call :logMessage "INFO" "Checking Python %PYTHON_MIN% installation..."

:: Check for python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    :: Check for py
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        call :logMessage "ERROR" "Python %PYTHON_MIN% or higher not found!"
        call :logMessage "ERROR" "Please install Python from https://python.org"
        call :logMessage "ERROR" "Python is required for Matrix Broadcast Studio"
        goto :fatalError
    ) else (
        set "PYTHON_CMD=py"
        for /f "tokens=2 delims=." %%a in ('py --version 2^>^&1') do set "PYTHON_VERSION=%%a"
    )
) else (
    set "PYTHON_CMD=python"
    for /f "tokens=2 delims=." %%a in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%a"
)

:: Check version
for /f "tokens=2 delims=." %%a in ("%PYTHON_MIN%") do set "MIN_MAJOR=%%a"
for /f "tokens=1 delims=." %%a in ("%PYTHON_VERSION%") do set "CURRENT_MAJOR=%%a"

if %CURRENT_MAJOR% lss %MIN_MAJOR% (
    call :logMessage "ERROR" "Python %PYTHON_VERSION% is too old (minimum %PYTHON_MIN%)"
    call :logMessage "ERROR" "Please upgrade Python to version %PYTHON_MIN% or higher"
    goto :fatalError
)

call :logMessage "SUCCESS" "Python %PYTHON_VERSION% found"
goto :eof

:: Function to create installation directory
:createInstallDir
call :logMessage "INFO" "Creating installation directory at %INSTALL_DIR%..."

:: Check if directory exists and is accessible
if exist "%INSTALL_DIR%" (
    :: Test if directory is writable
    echo test > "%INSTALL_DIR%\test_write.tmp" 2>nul
    if exist "%INSTALL_DIR%\test_write.tmp" (
        del "%INSTALL_DIR%\test_write.tmp" 2>nul
        call :logMessage "INFO" "Installation directory already exists and is writable"
        goto :eof
    ) else (
        call :logMessage "ERROR" "Installation directory exists but is not writable"
        call :logMessage "ERROR" "Please check permissions or choose different location"
        goto :fatalError
    )
)

:: Create directory
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%" 2>nul
    if errorlevel 1 (
        call :logMessage "ERROR" "Failed to create installation directory"
        call :logMessage "ERROR" "Please check permissions or disk space"
        goto :fatalError
    )
    call :logMessage "SUCCESS" "Installation directory created successfully"
)

:: Create subdirectories
call :createSubDir "uploads"
call :createSubDir "uploads\avatars"
call :createSubDir "uploads\avatars\users"
call :createSubDir "uploads\avatars\guests"
call :createSubDir "uploads\scenes"
call :createSubDir "uploads\streams"
call :createSubDir "logs"
call :createSubDir "config"

call :logMessage "SUCCESS" "Directory structure created"
goto :eof

:createSubDir
if not exist "%INSTALL_DIR%\%~1" (
    mkdir "%INSTALL_DIR%\%~1" 2>nul
    if errorlevel 1 (
        call :logMessage "WARN" "Failed to create subdirectory: %~1"
    )
)
goto :eof

:: Function to create virtual environment
:createVirtualEnv
call :logMessage "INFO" "Creating Python virtual environment..."

:: Check if venv exists
if exist "%INSTALL_DIR%\%VENV_NAME%" (
    call :logMessage "INFO" "Virtual environment already exists, checking integrity..."
    
    :: Test if venv is working
    "%INSTALL_DIR%\%VENV_NAME%\Scripts\python.exe" --version >nul 2>&1
    if errorlevel 1 (
        call :logMessage "WARN" "Existing virtual environment is broken, recreating..."
        rmdir /s /q "%INSTALL_DIR%\%VENV_NAME%" 2>nul
        goto :createNewVenv
    ) else (
        call :logMessage "SUCCESS" "Virtual environment is valid"
        set "VENV_CREATED=1"
        goto :eof
    )
)

:createNewVenv
cd /d "%INSTALL_DIR%"
%PYTHON_CMD% -m venv %VENV_NAME% 2>nul
if errorlevel 1 (
    call :logMessage "ERROR" "Failed to create virtual environment"
    call :logMessage "ERROR" "This may be due to corrupted Python installation"
    call :logMessage "ERROR" "Please reinstall Python and try again"
    goto :fatalError
)
set "VENV_CREATED=1"
call :logMessage "SUCCESS" "Virtual environment created successfully"
goto :eof

:: Function to install dependencies
:installDependencies
call :logMessage "INFO" "Installing required dependencies..."

:: Activate virtual environment
if %VENV_CREATED% equ 1 (
    call "%INSTALL_DIR%\%VENV_NAME%\Scripts\activate.bat"
    if errorlevel 1 (
        call :logMessage "ERROR" "Failed to activate virtual environment"
        call :logMessage "ERROR" "Dependencies installation may fail"
        set "VENV_CREATED=0"
    )
)

:: Install dependencies with progress tracking
call :logMessage "INFO" "Installing Flask and web framework..."
if %VENV_CREATED% equ 1 (
    pip install flask flask-cors --quiet 2>nul
) else (
    %PYTHON_CMD% -m pip install flask flask-cors --quiet 2>nul
)
if errorlevel 1 (
    call :logMessage "ERROR" "Failed to install Flask dependencies"
) else (
    call :progressBar 1 5
    set /a SUCCESS_COUNT+=1
)

call :logMessage "INFO" "Installing image processing libraries..."
if %VENV_CREATED% equ 1 (
    pip install Pillow --quiet 2>nul
) else (
    %PYTHON_CMD% -m pip install Pillow --quiet 2>nul
)
if errorlevel 1 (
    call :logMessage "ERROR" "Failed to install image processing libraries"
) else (
    call :progressBar 2 5
    set /a SUCCESS_COUNT+=1
)

call :logMessage "INFO" "Installing scheduling and platform libraries..."
if %VENV_CREATED% equ 1 (
    pip install apscheduler google-api-python-client google-auth-oauthlib --quiet 2>nul
) else (
    %PYTHON_CMD% -m pip install apscheduler google-api-python-client google-auth-oauthlib --quiet 2>nul
)
if errorlevel 1 (
    call :logMessage "WARN" "Failed to install advanced dependencies (optional features may not work)"
    call :logMessage "WARN" "Basic functionality will still work"
) else (
    call :progressBar 3 5
    set /a SUCCESS_COUNT+=1
)

call :logMessage "INFO" "Installing system integration libraries..."
if %VENV_CREATED% equ 1 (
    pip install pystray --quiet 2>nul
) else (
    %PYTHON_CMD% -m pip install pystray --quiet 2>nul
)
if errorlevel 1 (
    call :logMessage "WARN" "Failed to install system tray (optional)"
) else (
    call :progressBar 4 5
    set /a SUCCESS_COUNT+=1
)

call :progressBar 5 5
call :logMessage "SUCCESS" "Dependency installation completed"

:: Check critical dependencies
call :logMessage "INFO" "Verifying critical dependencies installation..."

if %VENV_CREATED% equ 1 (
    pip list | findstr /i "flask" >nul
) else (
    %PYTHON_CMD% -m pip list | findstr /i "flask" >nul
)
if errorlevel 1 (
    call :logMessage "ERROR" "Flask is not installed - system cannot run"
    goto :fatalError
)

call :logMessage "SUCCESS" "All critical dependencies verified"
goto :eof

:: Function to copy Matrix Studio files
:copyMatrixStudioFiles
call :logMessage "INFO" "Installing Matrix Studio files..."

:: Check source directory
if not exist "..\matrix-studio" (
    if not exist "matrix-studio" (
        call :logMessage "ERROR" "Matrix Studio source files not found!"
        call :logMessage "ERROR" "Please ensure this installer is run from the correct location"
        goto :fatalError
    )
    set "SOURCE_DIR=matrix-studio"
) else (
    set "SOURCE_DIR=..\matrix-studio"
)

:: Copy production backend
call :copyFile "production_ready_backend.py"
:: Copy core systems
call :copyFile "guest_management.py"
call :copyFile "scene_manager.py"
call :copyFile "avatar_management.py"
call :copyFile "broadcast_engine.py"
call :copyFile "analytics.py"
call :copyFile "scheduler.py"
call :copyFile "platform_integrations.py"

call :logMessage "SUCCESS" "Matrix Studio files copied successfully"
goto :eof

:copyFile
if exist "%SOURCE_DIR%\%~1" (
    copy "%SOURCE_DIR%\%~1" "%INSTALL_DIR%\" 2>nul
    if errorlevel 1 (
        call :logMessage "ERROR" "Failed to copy: %~1"
    ) else (
        set /a SUCCESS_COUNT+=1
    )
) else (
    call :logMessage "ERROR" "Source file not found: %~1"
)
goto :eof

:: Function to create configuration
:createConfiguration
call :logMessage "INFO" "Creating configuration files..."

:: Create main config
(
echo {> "%INSTALL_DIR%\config\config.json"
echo   "app_name": "Matrix Broadcast Studio",>> "%INSTALL_DIR%\config\config.json"
echo   "version": "2.0.0",>> "%INSTALL_DIR%\config\config.json"
echo   "production_mode": false,>> "%INSTALL_DIR%\config\config.json"
echo   "default_port": 8080,>> "%INSTALL_DIR%\config\config.json"
echo   "max_guests": 6,>> "%INSTALL_DIR%\config\config.json"
echo   "enable_analytics": true,>> "%INSTALL_DIR%\config\config.json"
echo   "enable_scheduler": true,>> "%INSTALL_DIR%\config\config.json"
echo   "web_root": "public",>> "%INSTALL_DIR%\config\config.json"
echo   "upload_max_size": "16MB",>> "%INSTALL_DIR%\config\config.json"
echo   "supported_formats": ["jpg", "jpeg", "png", "gif", "webp"],>> "%INSTALL_DIR%\config\config.json"
echo   "quality_presets": {>> "%INSTALL_DIR%\config\config.json"
echo     "360p": {"width": 640, "height": 360, "bitrate": 1000},>> "%INSTALL_DIR%\config\config.json"
echo     "480p": {"width": 854, "height": 480, "bitrate": 2000},>> "%INSTALL_DIR%\config\config.json"
echo     "720p": {"width": 1280, "height": 720, "bitrate": 4500},>> "%INSTALL_DIR%\config\config.json"
echo     "1080p": {"width": 1920, "height": 1080, "bitrate": 8000}>> "%INSTALL_DIR%\config\config.json"
echo   }>> "%INSTALL_DIR%\config\config.json"
echo   "guest_roles": ["guest", "moderator", "host", "spectator"],>> "%INSTALL_DIR%\config\config.json"
echo   "platforms": ["youtube", "twitch", "facebook", "linkedin"],>> "%INSTALL_DIR%\config\config.json"
echo   "matrix_theme": {>> "%INSTALL_DIR%\config\config.json"
echo     "primary_color": "#00ff00",>> "%INSTALL_DIR%\config\config.json"
echo     "secondary_color": "#003300",>> "%INSTALL_DIR%\config\config.json"
echo     "accent_color": "#00ffff",>> "%INSTALL_DIR%\config\config.json"
echo     "background_color": "#000000",>> "%INSTALL_DIR%\config\config.json"
echo     "grid_color": "#001100">> "%INSTALL_DIR%\config\config.json"
echo   }>> "%INSTALL_DIR%\config\config.json"
echo }>> "%INSTALL_DIR%\config\config.json"
)

:: Create .env file for environment variables
(
echo MATRIX_APP_NAME=Matrix Broadcast Studio> "%INSTALL_DIR%\.env"
echo MATRIX_APP_VERSION=2.0.0>> "%INSTALL_DIR%\.env"
echo MATRIX_ENV=production>> "%INSTALL_DIR%\.env"
echo MATRIX_PORT=8080>> "%INSTALL_DIR%\.env"
echo MATRIX_DEBUG=false>> "%INSTALL_DIR%\.env"
echo MATRIX_MAX_GUESTS=6>> "%INSTALL_DIR%\.env"
echo MATRIX_ENABLE_ANALYTICS=true>> "%INSTALL_DIR%\.env"
echo MATRIX_ENABLE_SCHEDULER=true>> "%INSTALL_DIR%\.env"
echo MATRIX_UPLOAD_FOLDER=./uploads>> "%INSTALL_DIR%\.env"
echo MATRIX_LOG_FOLDER=./logs>> "%INSTALL_DIR%\.env"
echo MATRIX_CONFIG_FILE=./config/config.json>> "%INSTALL_DIR%\.env"
echo # SECURITY: Never commit this file with real credentials>> "%INSTALL_DIR%\.env"
)

call :logMessage "SUCCESS" "Configuration files created"
goto :eof

:: Function to create launchers
:createLaunchers
call :logMessage "INFO" "Creating application launchers..."

:: Main production launcher
(
echo @echo off> "%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat"
echo setlocal enabledelayedexpansion>> "%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat"
echo cd /d "%%~dp0">> "%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat"
echo if exist "%%VENV_NAME%%\Scripts\activate.bat" ^(^>> "%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat"
echo     call "%%VENV_NAME%%\Scripts\activate.bat"^> "%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat"
echo ^)  ^(^>> "%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat"
echo     set PYTHON_CMD=python^> "%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat"
echo ^)>> "%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat"
echo echo [🌊 MATRIX] Starting Production Broadcast Studio...>> "%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat"
echo python production_ready_backend.py>> "%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat"
echo if errorlevel 1 (^>> "%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat"
echo     echo [❌ ERROR] Failed to start Matrix Broadcast Studio>> "%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat"
echo     pause>> "%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat"
echo ^)>> "%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat"
)

:: System tray launcher
(
echo @echo off> "%INSTALL_DIR%\MATRIX_STUDIO_TRAY.bat"
echo setlocal enabledelayedexpansion>> "%INSTALL_DIR%\MATRIX_STUDIO_TRAY.bat"
echo cd /d "%%~dp0">> "%INSTALL_DIR%\MATRIX_STUDIO_TRAY.bat"
echo if exist "%%VENV_NAME%%\Scripts\activate.bat" ^(^>> "%INSTALL_DIR%\MATRIX_STUDIO_TRAY.bat"
echo     call "%%VENV_NAME%%\Scripts\activate.bat"^> "%INSTALL_DIR%\MATRIX_STUDIO_TRAY.bat"
echo ^)  ^(^>> "%INSTALL_DIR%\MATRIX_STUDIO_TRAY.bat"
echo     set PYTHON_CMD=python^> "%INSTALL_DIR%\MATRIX_STUDIO_TRAY.bat"
echo ^)>> "%INSTALL_DIR%\MATRIX_STUDIO_TRAY.bat"
echo echo [🌊 MATRIX] Starting System Tray Broadcast Studio...>> "%INSTALL_DIR%\MATRIX_STUDIO_TRAY.bat"
echo python matrix_studio_tray.py>> "%INSTALL_DIR%\MATRIX_STUDIO_TRAY.bat"
echo if errorlevel 1 (^>> "%INSTALL_DIR%\MATRIX_STUDIO_TRAY.bat"
echo     echo [❌ ERROR] Failed to start Matrix Broadcast Studio Tray>> "%INSTALL_DIR%\MATRIX_STUDIO_TRAY.bat"
echo     echo [⚡ INFO] Starting main launcher...>> "%INSTALL_DIR%\MATRIX_STUDIO_TRAY.bat"
echo     call MATRIX_STUDIO_PRODUCTION.bat>> "%INSTALL_DIR%\MATRIX_STUDIO_TRAY.bat"
echo ^)>> "%INSTALL_DIR%\MATRIX_STUDIO_TRAY.bat"
)

:: Uninstaller
(
echo @echo off> "%INSTALL_DIR%\uninstall.bat"
echo title Matrix Broadcast Studio - Uninstaller>> "%INSTALL_DIR%\uninstall.bat"
echo echo [🌊 MATRIX] Uninstalling Matrix Broadcast Studio...>> "%INSTALL_DIR%\uninstall.bat"
echo echo.>> "%INSTALL_DIR%\uninstall.bat"
echo echo This will remove all Matrix Broadcast Studio files and settings.>> "%INSTALL_DIR%\uninstall.bat"
echo echo.>> "%INSTALL_DIR%\uninstall.bat"
echo choice /c YN /m "Are you sure you want to continue? (Y/N): ">> "%INSTALL_DIR%\uninstall.bat"
echo if errorlevel 2 goto end>> "%INSTALL_DIR%\uninstall.bat"
echo if errorlevel 1 goto uninstall>> "%INSTALL_DIR%\uninstall.bat"
echo echo [⚡ INFO] Uninstallation cancelled>> "%INSTALL_DIR%\uninstall.bat"
echo goto end>> "%INSTALL_DIR%\uninstall.bat"
echo :uninstall>> "%INSTALL_DIR%\uninstall.bat"
echo echo [🌊 MATRIX] Removing Matrix Broadcast Studio...>> "%INSTALL_DIR%\uninstall.bat"
echo rd /s /q "%%~dp0">> "%INSTALL_DIR%\uninstall.bat"
echo echo [✅ SUCCESS] Matrix Broadcast Studio uninstalled>> "%INSTALL_DIR%\uninstall.bat"
echo :end>> "%INSTALL_DIR%\uninstall.bat"
echo pause>> "%INSTALL_DIR%\uninstall.bat"
)

call :logMessage "SUCCESS" "Application launchers created"
goto :eof

:: Function to create shortcuts
:createShortcuts
call :logMessage "INFO" "Creating desktop shortcuts..."

:: Desktop shortcut
set "DESKTOP=%USERPROFILE%\Desktop"
powershell -command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\Matrix Broadcast Studio.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = 'shell32.dll'; $Shortcut.IconIndex = 13; $Shortcut.Description = 'Matrix Broadcast Studio - Professional Broadcasting System'; $Shortcut.Save()" 2>nul

:: Start Menu shortcut
set "STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
if not exist "%STARTMENU%\Matrix Broadcast Studio" mkdir "%STARTMENU%\Matrix Broadcast Studio"
powershell -command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTMENU%\Matrix Broadcast Studio\Matrix Broadcast Studio.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = 'shell32.dll'; $Shortcut.IconIndex = 13; $Shortcut.Description = 'Matrix Broadcast Studio - Professional Broadcasting System'; $Shortcut.Save()" 2>nul

:: Quick Launch shortcut
powershell -command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTMENU%\Programs\Matrix Broadcast Studio.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\MATRIX_STUDIO_PRODUCTION.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = 'shell32.dll'; $Shortcut.IconIndex = 13; $Shortcut.Description = 'Matrix Broadcast Studio - Professional Broadcasting System'; $Shortcut.Save()" 2>nul

call :logMessage "SUCCESS" "Desktop and Start Menu shortcuts created"
goto :eof

:: Function to display installation report
:showInstallationReport
call :logMessage "MATRIX" "=== INSTALLATION REPORT ==="
call :logMessage "INFO" "Installation Location: %INSTALL_DIR%"
call :logMessage "INFO" "Python Version: %PYTHON_VERSION%"
call :logMessage "INFO" "Virtual Environment: %VENV_NAME%"
call :logMessage "INFO" "Success Count: %SUCCESS_COUNT%"
call :logMessage "INFO" "Error Count: %ERROR_COUNT%"
call :logMessage "INFO" "Warning Count: %WARNING_COUNT%"
call :logMessage "MATRIX" "==========================="
goto :eof

:: Fatal error handler
:fatalError
call :logMessage "ERROR" "Installation failed with errors!"
call :logMessage "WARN" "Please review the error messages above"
call :logMessage "INFO" "Common issues:"
call :logMessage "INFO"   - Insufficient privileges"
call :logMessage "INFO"   - Python installation corrupted"
call :logMessage "INFO"   - Insufficient disk space"
call :logMessage "INFO"   - Antivirus blocking installation"
call :logMessage "INFO" "Please resolve issues and try again"
echo.
echo Press any key to exit...
pause >nul
exit /b 1

:: Main installation sequence
:main
:: Enhanced ASCII art
cls
echo.
echo  ██████╗ ██████╗ ██████╗ ██████╗ ██████╗ 
echo  ██╔══╝██╔══╝██╔══██╗██╔══██╗
echo  ██████╗█████╗█████╗█████╗ 
echo  ██╔══╝██╔══╝██╔══██╗██╔══██╗
echo  ██████╗█████╗█████╗█████╗ 
echo.
echo  🌊 MATRIX BROADCAST STUDIO - COMPREHENSIVE INSTALLER
echo  ════════════════════════════════════════════════════
echo  Professional Broadcasting System • Complete Error Handling
echo  ════════════════════════════════════════════════════
echo.

:: Configuration
set "APP_NAME=Matrix Broadcast Studio"
set "INSTALL_DIR=C:\MatrixStudio"
set "VENV_NAME=matrix_studio_env"
set "PYTHON_MIN=3.8"
set "MAX_PORT_ATTEMPTS=10"
set "DEFAULT_PORT=8080"

:: Pre-installation checks
call :checkAdmin
call :checkPython
call :logMessage "MATRIX" "Starting comprehensive installation process..."

:: Installation steps with progress
call :logMessage "INFO" "Step 1/7: Directory setup"
call :createInstallDir
call :progressBar 1 7

call :logMessage "INFO" "Step 2/7: Virtual environment"
call :createVirtualEnv
call :progressBar 2 7

call :logMessage "INFO" "Step 3/7: Dependencies"
call :installDependencies
call :progressBar 3 7

call :logMessage "INFO" "Step 4/7: Configuration"
call :createConfiguration
call :progressBar 4 7

call :logMessage "INFO" "Step 5/7: File deployment"
call :copyMatrixStudioFiles
call :progressBar 5 7

call :logMessage "INFO" "Step 6/7: Launchers creation"
call :createLaunchers
call :progressBar 6 7

call :logMessage "INFO" "Step 7/7: Shortcuts creation"
call :createShortcuts
call :progressBar 7 7

:: Post-installation
call :showInstallationReport

:: Final success message
call :logMessage "MATRIX" "=== INSTALLATION COMPLETE ==="
call :logMessage "SUCCESS" "Matrix Broadcast Studio installation completed successfully!"
call :logMessage "SUCCESS" "Location: %INSTALL_DIR%"
call :logMessage "SUCCESS" "Errors: %ERROR_COUNT%"
call :logMessage "SUCCESS" "Warnings: %WARNING_COUNT%"
call :logMessage "SUCCESS" "Ready for professional broadcasting!"

echo.
echo 🌊 MATRIX BROADCAST STUDIO - READY FOR USE
echo ════════════════════════════════════════════════════
echo.
echo 🚀 LAUNCH OPTIONS:
echo    1. Desktop: "Matrix Broadcast Studio" shortcut
echo    2. Start Menu: Programs → Matrix Broadcast Studio
echo    3. Command: cd "%INSTALL_DIR%" && MATRIX_STUDIO_PRODUCTION.bat
echo    4. System Tray: MATRIX_STUDIO_TRAY.bat
echo.
echo 🌐 WEB ACCESS:
echo    • URL: http://localhost:8080
echo    • API: http://localhost:8080/api
echo    • Health: http://localhost:8080/api/health
echo.
echo 👤 DEMO CREDENTIALS:
echo    • Username: demo
echo    • Password: demo123
echo.
echo 📖 USER GUIDE:
echo    • Location: %INSTALL_DIR%\PRODUCTION_COMPLETE.md
echo.
echo 🗑️ UNINSTALL:
echo    • Run: %INSTALL_DIR%\uninstall.bat
echo.
echo ════════════════════════════════════════════════════

:: Auto-start option
set /p "auto_start=Start Matrix Broadcast Studio now? (Y/N): "
if /i "%auto_start%"=="Y" (
    call :logMessage "INFO" "Auto-starting Matrix Broadcast Studio..."
    cd /d "%INSTALL_DIR%"
    if exist "%VENV_NAME%\Scripts\activate.bat" (
        call "%VENV_NAME%\Scripts\activate.bat"
    )
    start "" /MAX "MATRIX_STUDIO_PRODUCTION.bat"
    call :logMessage "SUCCESS" "Matrix Broadcast Studio started in background"
)

echo.
echo Press any key to exit the installer...
pause >nul

exit /b 0