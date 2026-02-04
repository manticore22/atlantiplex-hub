@echo off
title Atlantiplex Lightning Studio - Complete Launch Script
color 0a
mode 100,30

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                 ATLANTIPLEX LIGHTNING STUDIO                   ║
echo  ║            Professional Broadcasting Platform v2.0                ║
echo  ║                Debug, Test, Refine - Complete                  ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

echo [1/5] Starting Frontend Development Server...
cd "matrix-studio\web\frontend"
start "Frontend" cmd /k "npm run dev"

echo [2/5] Starting Backend Production Server...
cd "..\..\.."
start "Backend" cmd /k "cd matrix-studio && python run.py"

echo [3/5] Opening Test Page...
start "Test" cmd /k "echo Opening test page... && timeout /t 3 && start http://localhost:5173 && echo Test page opened successfully!"

echo [4/5] Opening Main Application...
timeout /t 5
start http://localhost:8080

echo [5/5] Opening Static Interface...
timeout /t 2
start http://localhost:8080/static/index.html

echo.
echo  ══════════════════════════════════════════════════════════════
echo  🚀 ATLANTIPLEX LIGHTNING STUDIO - LAUNCHED SUCCESSFULLY!
echo.
echo  📍 Access Points:
echo     • Frontend Dev:    http://localhost:5173
echo     • Backend API:     http://localhost:8080
echo     • Static Interface: http://localhost:8080/static/index.html
echo     • Test Page:       test-studio.html (double-click)
echo.
echo  🔐 Login Credentials:
echo     • Username: demo
echo     • Password: demo123
echo.
echo  ✨ Features:
echo     • ⚡ Lightning in bottle logo
echo     • 🎨 Modern glassmorphism UI
echo     • 📱 Responsive design
echo     • 🎬 Scene management
echo     • 👥 Guest controls (6 slots)
echo     • 📺 Broadcasting capabilities
echo.
echo  Press any key to exit this launcher...
pause >nul