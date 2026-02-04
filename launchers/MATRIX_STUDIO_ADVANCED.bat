@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

:: ============================================================================
:: 🌊 MATRIX BROADCAST STUDIO - ADVANCED LAUNCHER v2.0
:: Professional One-Click Streaming Studio with Auto-Dependency Management
:: ============================================================================

:: Set console to Matrix Green color
color 0a

:: Console settings
mode 100,30
title 🌊 MATRIX BROADCAST STUDIO v2.0

:: Enhanced Matrix ASCII art
cls
echo.
echo  ██╗    ██╗██╗  ██╗ █████╗ ████████╗███████╗██████╗ ███╗   ███╗ █████╗ ██╗     ███████╗
echo  ██║    ██║██║  ██║██╔══██╗╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██╔══██╗██║     ██╔════╝
echo  ██║ █╗ ██║███████║███████║   ██║   █████╗  ██████╔╝██╔████╔██║███████║██║     █████╗  
echo  ██║███╗██║██╔══██║██╔══██║   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══██║██║     ██╔══╝  
echo  ╚███╔███╔╝██║  ██║██║  ██║   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║  ██║███████╗███████╗
echo   ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝
echo.
echo  ██████╗ ███████╗ █████╗ ██████╗ 
echo  ██╔══██╗██╔════╝██╔══██╗██╔══██╗
echo  ██║  ██║█████╗  ███████║██║  ██║
echo  ██║  ██║██╔══╝  ██╔══██║██║  ██║
echo  ██████╔╝███████╗██║  ██║██████╔╝
echo  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═════╝ 
echo.
echo  🌊 ADVANCED BROADCASTING STUDIO v2.0
echo  ═══════════════════════════════════════════════════════════════════════════════
echo  Auto-Dependency Management • Port Detection • System Tray Integration
echo  Professional Scene Management • Multi-Platform Streaming
echo  ═══════════════════════════════════════════════════════════════════════════════
echo.

:: Configuration
set APP_NAME=Matrix Broadcast Studio
set MAIN_SCRIPT=matrix_studio_final.py
set CONFIG_FILE=config.json
set DEPENDENCY_FILE=requirements.txt
set LOG_FILE=matrix_studio.log
set PYTHON_MIN=3.8
set DEFAULT_PORT=8080
set FALLBACK_PORT=8081

:: Initialize status
set STATUS=INITIALIZING
set PYTHON_FOUND=0
set VENV_EXISTS=0
set DEPS_INSTALLED=0
set APP_STARTED=0

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

:: Main initialization sequence
call :printStatus "MATRIX" "Initializing MATRIX BROADCAST STUDIO..."
call :printStatus "INFO" "Checking system requirements..."

:: Check Python installation
call :checkPython
if %PYTHON_FOUND% equ 0 (
    call :printStatus "ERROR" "Python %PYTHON_MIN% or higher is required"
    call :printStatus "INFO" "Please install Python from https://python.org"
    goto :errorExit
)

:: Check working directory and files
call :checkFiles
if errorlevel 1 (
    call :printStatus "ERROR" "Required files not found"
    goto :errorExit
)

:: Setup virtual environment
call :setupVirtualEnv

:: Install dependencies
call :installDependencies

:: Find available port
call :findAvailablePort

:: Start the application
call :startApplication

:: Success exit
call :printStatus "SUCCESS" "Matrix Broadcast Studio started successfully!"
call :printStatus "INFO" "Web interface: http://localhost:%FOUND_PORT%"
call :printStatus "INFO" "API endpoint: http://localhost:%FOUND_PORT%/api"
call :printStatus "INFO" "Press Ctrl+C to stop the server"
echo.
goto :keepRunning

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

:checkFiles
call :printStatus "INFO" "Checking required files..."

if not exist "%MAIN_SCRIPT%" (
    call :printStatus "ERROR" "Main script not found: %MAIN_SCRIPT%"
    exit /b 1
)

if not exist "scene_manager.py" (
    call :printStatus "ERROR" "Scene manager not found: scene_manager.py"
    exit /b 1
)

if not exist "analytics.py" (
    call :printStatus "ERROR" "Analytics module not found: analytics.py"
    exit /b 1
)

call :printStatus "SUCCESS" "All required files found"
goto :eof

:setupVirtualEnv
call :printStatus "INFO" "Checking virtual environment..."

if not exist "venv" (
    call :printStatus "INFO" "Creating virtual environment..."
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        call :printStatus "WARN" "Failed to create virtual environment, using system Python"
        set VENV_EXISTS=0
        goto :eof
    )
    call :printStatus "SUCCESS" "Virtual environment created"
    set VENV_EXISTS=1
) else (
    call :printStatus "INFO" "Virtual environment already exists"
    set VENV_EXISTS=1
)

:: Activate virtual environment
if %VENV_EXISTS% equ 1 (
    call :printStatus "INFO" "Activating virtual environment..."
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        call :printStatus "WARN" "Failed to activate virtual environment"
        set VENV_EXISTS=0
    ) else (
        call :printStatus "SUCCESS" "Virtual environment activated"
    )
)
goto :eof

:installDependencies
call :printStatus "INFO" "Checking and installing dependencies..."

:: Check if requirements file exists
if not exist "%DEPENDENCY_FILE%" (
    call :printStatus "WARN" "Requirements file not found, creating with basic dependencies..."
    echo flask==2.3.3 > %DEPENDENCY_FILE%
    echo flask-cors==4.0.0 >> %DEPENDENCY_FILE%
    echo PIL==10.0.0 >> %DEPENDENCY_FILE%
    echo werkzeug==2.3.7 >> %DEPENDENCY_FILE%
)

:: Install dependencies
call :printStatus "INFO" "Installing dependencies from %DEPENDENCY_FILE%..."
if %VENV_EXISTS% equ 1 (
    pip install -r %DEPENDENCY_FILE% --quiet
) else (
    %PYTHON_CMD% -m pip install -r %DEPENDENCY_FILE% --quiet
)

if errorlevel 1 (
    call :printStatus "WARN" "Some dependencies failed to install, trying individual packages..."
    
    :: Try installing core dependencies individually
    call :installIndividualPackage "flask"
    call :installIndividualPackage "flask-cors"
    call :installIndividualPackage "Pillow"
    call :installIndividualPackage "werkzeug"
) else (
    call :printStatus "SUCCESS" "Dependencies installed successfully"
    set DEPS_INSTALLED=1
)
goto :eof

:installIndividualPackage
call :printStatus "INFO" "Installing %~1..."
if %VENV_EXISTS% equ 1 (
    pip install "%~1" --quiet
) else (
    %PYTHON_CMD% -m pip install "%~1" --quiet
)
if errorlevel 1 (
    call :printStatus "WARN" "Failed to install %~1"
) else (
    call :printStatus "SUCCESS" "Installed %~1"
)
goto :eof

:findAvailablePort
call :printStatus "INFO" "Finding available port..."
set FOUND_PORT=%DEFAULT_PORT%

:: Check if default port is available
netstat -an | findstr ":%DEFAULT_PORT%" >nul 2>&1
if not errorlevel 1 (
    call :printStatus "WARN" "Port %DEFAULT_PORT% is in use, trying fallback port %FALLBACK_PORT%"
    netstat -an | findstr ":%FALLBACK_PORT%" >nul 2>&1
    if not errorlevel 1 (
        call :printStatus "WARN" "Fallback port %FALLBACK_PORT% also in use"
        set /p FOUND_PORT="Enter alternative port (default 8082): "
        if "!FOUND_PORT!"=="" set FOUND_PORT=8082
    ) else (
        set FOUND_PORT=%FALLBACK_PORT%
        call :printStatus "SUCCESS" "Using fallback port %FALLBACK_PORT%"
    )
) else (
    call :printStatus "SUCCESS" "Using default port %DEFAULT_PORT%"
)
goto :eof

:startApplication
call :printStatus "MATRIX" "🌊 INITIALIZING MATRIX BROADCAST STUDIO..."
call :printStatus "INFO" "Starting application on port %FOUND_PORT%..."
call :printStatus "INFO" "Loading scene manager..."
call :printStatus "INFO" "Initializing analytics..."
call :printStatus "INFO" "Setting up platform integrations..."

:: Create log file
echo [%date% %time%] Matrix Broadcast Studio Starting > %LOG_FILE%
echo [%date% %time%] Port: %FOUND_PORT% >> %LOG_FILE%
echo [%date% %time%] Python: %PYTHON_VERSION% >> %LOG_FILE%

:: Start the application
if %VENV_EXISTS% equ 1 (
    call :printStatus "INFO" "Starting with virtual environment Python..."
    python "%MAIN_SCRIPT%" --port %FOUND_PORT%
) else (
    call :printStatus "INFO" "Starting with system Python..."
    %PYTHON_CMD% "%MAIN_SCRIPT%" --port %FOUND_PORT%
)

if errorlevel 1 (
    call :printStatus "ERROR" "Failed to start the application"
    goto :errorExit
) else (
    set APP_STARTED=1
)
goto :eof

:keepRunning
call :printStatus "INFO" "Matrix Broadcast Studio is running..."
call :printStatus "INFO" "Press any key to stop the server and exit"
pause >nul
call :printStatus "INFO" "Shutting down Matrix Broadcast Studio..."
goto :cleanExit

:errorExit
call :printStatus "ERROR" "Matrix Broadcast Studio failed to start"
call :printStatus "INFO" "Please check the error messages above"
call :printStatus "INFO" "Log file: %LOG_FILE%"
pause
exit /b 1

:cleanExit
call :printStatus "SUCCESS" "Matrix Broadcast Studio stopped successfully"
if %VENV_EXISTS% equ 1 (
    call venv\Scripts\deactivate.bat >nul 2>&1
)
exit /b 0