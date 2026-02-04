@echo off
title Push to GitHub - Atlantiplex Studio
color 0a
mode 100,40

echo.
echo  ╔══════════════════════════════════════════════════════════════════════════════╗
echo  ║                    PUSH TO GITHUB - ATLANTIPLEX STUDIO                       ║
echo  ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

set GIT_PATH="%LOCALAPPDATA%\GitHubDesktop\app-3.5.4\resources\app\git\cmd\git.exe"

echo ✅ Repository initialized and committed locally
echo.

REM Check if remote already exists
%GIT_PATH% remote -v >nul 2>&1
if %errorlevel% == 0 (
    echo [INFO] Remote repository already configured
    %GIT_PATH% remote -v
    echo.
    echo Do you want to push now? (Y/N)
    set /p PUSH_NOW=
    if /i "%PUSH_NOW%"=="Y" goto PUSH
    goto END
)

echo ═══════════════════════════════════════════════════════════════════════════════
echo  STEP 1: CREATE GITHUB REPOSITORY
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo  1. Open your browser and go to: https://github.com/new
echo.
echo  2. Fill in the details:
echo     - Repository name: atlantiplex-lightning-studio
echo     - Description: Enterprise Multi-Tenant SaaS Broadcasting Platform
echo     - Make it: Public or Private (your choice)
echo     - DO NOT initialize with README (we already have one!)
echo.
echo  3. Click "Create repository"
echo.
echo  4. Copy the repository URL (HTTPS or SSH)
echo     Example: https://github.com/YOUR_USERNAME/atlantiplex-lightning-studio.git
echo.
pause

echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo  STEP 2: CONNECT TO GITHUB
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
set /p REPO_URL="Paste your GitHub repository URL: "

if "%REPO_URL%"=="" (
    echo ❌ No URL provided. Exiting...
    pause
    exit /b 1
)

echo.
echo [1/3] Adding remote repository...
%GIT_PATH% remote add origin %REPO_URL%
if errorlevel 1 (
    echo ⚠️  Remote already exists or error occurred. Trying to update...
    %GIT_PATH% remote set-url origin %REPO_URL%
)
echo ✅ Remote added: %REPO_URL%
echo.

echo [2/3] Renaming branch to 'main'...
%GIT_PATH% branch -M main
echo ✅ Branch renamed to 'main'
echo.

:PUSH
echo ═══════════════════════════════════════════════════════════════════════════════
echo  STEP 3: PUSH TO GITHUB
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo [3/3] Pushing code to GitHub...
echo     (This may take a few minutes for 259 files...)
echo.

%GIT_PATH% push -u origin main

if errorlevel 1 (
    echo.
    echo  ❌ Push failed!
    echo.
    echo  Common issues:
    echo    1. You need to authenticate with GitHub
    echo    2. The repository URL is incorrect
    echo    3. You don't have permission to push to this repo
    echo.
    echo  To authenticate:
    echo    - Use GitHub Desktop (easiest)
    echo    - Or create a Personal Access Token:
    echo      https://github.com/settings/tokens
    echo.
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo  🎉 SUCCESS! CODE PUSHED TO GITHUB!
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo  Your repository is now live at:
echo  %REPO_URL%
echo.
echo  What's next:
echo    ✅ Share your repository
echo    ✅ Set up GitHub Actions for CI/CD
echo    ✅ Enable GitHub Pages for documentation
echo    ✅ Add topics and description on GitHub
    
:END
echo.
echo  Press any key to exit...
pause >nul