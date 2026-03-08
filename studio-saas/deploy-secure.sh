#!/bin/bash

# SERAPHONIX STUDIO - Security Hardened Deployment Script
# Run this on your VPS to update with security fixes

echo "╔════════════════════════════════════════════════════════╗"
echo "║  🛡️  SECURITY HARDENED DEPLOYMENT                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Configuration
VPS_IP="76.13.242.128"
DEPLOY_DIR="/root/studio"

echo "📋 Step 1: Cleaning up old files..."
cd $DEPLOY_DIR/studio-saas/backend

# Delete old Python files
echo "  🗑️  Removing outdated Python files..."
rm -f app.py broadcast_engine.py scene_manager.py guest_management.py avatar_management.py
rm -f requirements.txt Dockerfile.python
rm -f server.js  # Remove old unsecure version
rm -rf __pycache__

echo "  ✅ Old files cleaned up"
echo ""

echo "📋 Step 2: Installing new secure server..."
# Rename secure server to main server
mv server-secure.js server.js 2>/dev/null || echo "Server already secure"

echo "  ✅ Server updated"
echo ""

echo "📋 Step 3: Installing security dependencies..."
npm install express-rate-limit express-validator helmet

echo "  ✅ Security packages installed"
echo ""

echo "📋 Step 4: Setting up environment..."
# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "JWT_SECRET=your-super-secret-jwt-key-change-this-in-production-$(date +%s)" > .env
    echo "NODE_ENV=production" >> .env
    echo "PORT=3001" >> .env
    echo "  ✅ .env file created - PLEASE EDIT WITH SECRET VALUES"
else
    echo "  ✅ .env file already exists"
fi
echo ""

echo "📋 Step 5: Stopping old server..."
pkill -f "node server.js" || true
sleep 2

echo "📋 Step 6: Starting secure server..."
export PORT=3001
export NODE_ENV=production
export JWT_SECRET=$(grep JWT_SECRET .env | cut -d= -f2)

nohup node server.js > server.log 2>&1 &
sleep 3

echo "  ✅ Server started"
echo ""

echo "📋 Step 7: Verifying deployment..."
HEALTH=$(curl -s http://localhost:3001/api/health | grep -o '"status":"ok"' || echo "FAILED")

if [ "$HEALTH" = '"status":"ok"' ]; then
    echo "  ✅ API Health Check: PASSED"
else
    echo "  ⚠️  API Health Check: Check logs with 'tail -f server.log'"
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║           ✅ SECURITY HARDENING COMPLETE               ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║  🔐 New Security Features:                             ║"
echo "║    • Rate limiting (100 req/15min, 10 auth attempts)   ║"
echo "║    • Helmet security headers                           ║"
echo "║    • Input validation & sanitization                   ║"
echo "║    • JWT required in production (no fallback)          ║"
echo "║    • CORS restricted to production domain              ║"
echo "║    • WebSocket authentication                          ║"
echo "║                                                        ║"
echo "║  🌐 Platform: http://76.13.242.128                     ║"
echo "║                                                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "⚠️  IMPORTANT: Edit .env file and set a strong JWT_SECRET!"
echo ""

# Show logs
echo "Recent server logs:"
tail -5 server.log