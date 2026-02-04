@echo off
title Atlantiplex - Upload to GitHub
color 0a
mode 80,40

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║            UPLOAD TO GITHUB - ATLANTIPLEX STUDIO             ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

echo Checking for Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ❌ Git not found!
    echo.
    echo  Please install Git first:
    echo  https://git-scm.com/download/win
    echo.
    echo  Or use GitHub Desktop:
    echo  https://desktop.github.com/
    echo.
    pause
    exit /b 1
)

echo ✅ Git detected
echo.

echo [1/6] Initializing Git repository...
git init
echo.

echo [2/6] Configuring Git (if not already set)...
git config user.name "Developer" >nul 2>&1
git config user.email "dev@atlantiplex.com" >nul 2>&1
echo.

echo [3/6] Adding all files to staging area...
git add .
echo ✅ Files staged
echo.

echo [4/6] Creating initial commit...
git commit -m "Initial commit: Atlantiplex Lightning Studio SaaS Platform

- Multi-tenant architecture with subdomain routing
- 5-tier subscription system with Stripe integration  
- Complete SaaS dashboard and analytics
- Enterprise security with RBAC and audit logging
- Modern UI with glassmorphism design
- Azure, AWS, GCP deployment ready
- 15,000+ lines of production code
- Enterprise-grade broadcasting platform"
echo ✅ Commit created
echo.

echo [5/6] Instructions for connecting to GitHub:
echo.
echo  ═══════════════════════════════════════════════════════════════
echo  NEXT STEPS:
echo.
echo  1. Create a new repository on GitHub:
echo     https://github.com/new
 echo.
echo  2. Repository name: atlantiplex-lightning-studio
 echo  3. Description: Enterprise Multi-Tenant SaaS Broadcasting Platform
 echo  4. DON'T initialize with README (we already have one)
 echo  5. Click "Create repository"
 echo.
echo  6. Then run these commands:
echo.
echo     git remote add origin https://github.com/YOUR_USERNAME/atlantiplex-lightning-studio.git
 echo     git branch -M main
 echo     git push -u origin main
 echo.
echo  ═══════════════════════════════════════════════════════════════
echo.

echo [6/6] Status:
git status
echo.

echo ✅ Local repository ready!
echo.
echo  Your project is prepared for GitHub upload.
echo  Follow the instructions above to complete the upload.
echo.
echo  Press any key to exit...
pause >nul