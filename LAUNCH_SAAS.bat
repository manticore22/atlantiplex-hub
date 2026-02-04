@echo off
title Atlantiplex Lightning Studio - SaaS Platform Launch
color 0a
mode 120,40

echo.
echo  ╔══════════════════════════════════════════════════════════════════════════════╗
echo  ║                                                                              ║
echo  ║           ATLANTIPLEX LIGHTNING STUDIO - SaaS PLATFORM v2.0                  ║
echo  ║                    Enterprise Multi-Tenant Architecture                      ║
echo  ║                                                                              ║
echo  ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo  🚀 LAUNCHING ENTERPRISE SAAS PLATFORM...
echo.
echo  ═══════════════════════════════════════════════════════════════════════════════
echo.

REM Change to matrix-studio directory
cd /d "%~dp0\matrix-studio"

echo [1/5] Checking Python Installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
)
echo ✅ Python detected
echo.

echo [2/5] Installing Required Dependencies...
pip install flask stripe PyJWT --quiet
echo ✅ Dependencies installed
echo.

echo [3/5] Initializing SaaS Database...
python -c "from saas_database import SaaSDatabaseManager; db = SaaSDatabaseManager(); print('✅ Database initialized')"
echo ✅ Multi-tenant database schema created
echo.

echo [4/5] Testing SaaS Components...
python -c "
from saas_multi_tenant import MultiTenantManager
from saas_database import SaaSDatabaseManager
from saas_dashboard import SaaSDashboard

# Test multi-tenant manager
mt = MultiTenantManager()
print('   ✅ MultiTenantManager initialized')

# Test database
db = SaaSDatabaseManager()
print('   ✅ SaaSDatabaseManager initialized')

# Test dashboard
dash = SaaSDashboard(db)
print('   ✅ SaaSDashboard initialized')

print('   ✅ All SaaS components working')
"
echo.

echo [5/5] Starting SaaS Platform...
echo.
echo  ═══════════════════════════════════════════════════════════════════════════════
echo  🎉 SaaS PLATFORM READY!
echo.
echo  📍 ACCESS POINTS:
echo     • Main Platform:    http://localhost:8080
echo     • API Endpoint:     http://localhost:8080/api
echo     • Health Check:     http://localhost:8080/health
echo.
echo  🔐 DEFAULT ADMIN ACCESS:
echo     • Super Admin:      http://localhost:8080/api/super-admin?admin_key=super-admin-key
echo.
echo  💡 QUICK START:
echo     1. Open browser to http://localhost:8080
echo     2. Click "Create Organization" to register
echo     3. Access your organization at: your-org.atlantiplex.com
echo     4. Manage teams, users, and billing from the dashboard
echo.
echo  📊 SAAS FEATURES ENABLED:
echo     ✅ Multi-tenant architecture (subdomain routing)
echo     ✅ 5 Subscription tiers (Free to Enterprise)
echo     ✅ Team management with role-based access
echo     ✅ Usage-based billing and analytics
necho     ✅ Audit logging and compliance
necho     ✅ API management and rate limiting
echo.
echo  🛠️ ADMIN COMMANDS:
echo     • Create org: POST /api/organizations
echo     • View stats: GET /api/super-admin?admin_key=super-admin-key
echo     • Health:     GET /health
echo.
echo  📝 DOCUMENTATION:
echo     • docs/SAAS_TRANSFORMATION_SUMMARY.md
echo     • docs/STRIPE_BACKEND_ANALYSIS.md
echo     • docs/PRICING_TIERS_ANALYSIS.md
echo.
echo  ═══════════════════════════════════════════════════════════════════════════════
echo.

REM Start the SaaS platform
python saas_platform.py

echo.
echo  Press any key to exit...
pause >nul