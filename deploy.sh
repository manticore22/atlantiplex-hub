#!/bin/bash

# SERAPHONIX STUDIO DEPLOYMENT SCRIPT
# Deploys the streaming platform to Hostinger VPS

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║     🎬 SERAPHONIX STUDIO DEPLOYMENT                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Configuration
VPS_IP="76.13.242.128"
VPS_USER="root"
DEPLOY_DIR="/root/studio"
REPO_URL="https://github.com/manticore22/Atlantiplex-studio-broadcasting.git"
API_PORT="3001"
WEB_PORT="80"

echo "📋 Deployment Configuration:"
echo "   VPS IP: $VPS_IP"
echo "   Deploy Directory: $DEPLOY_DIR"
echo "   API Port: $API_PORT"
echo "   Web Port: $WEB_PORT"
echo ""

# Check if SSH key exists
if [ ! -f ~/.ssh/seraphonix_deploy ]; then
    echo "🔑 Generating SSH key pair..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/seraphonix_deploy -N "" -C "deploy@seraphonix"
    echo ""
    echo "⚠️  IMPORTANT: Add this public key to your VPS authorized_keys:"
    cat ~/.ssh/seraphonix_deploy.pub
    echo ""
    echo "Run this on your VPS:"
    echo "  mkdir -p ~/.ssh && chmod 700 ~/.ssh"
    echo "  echo '$(cat ~/.ssh/seraphonix_deploy.pub)' >> ~/.ssh/authorized_keys"
    echo "  chmod 600 ~/.ssh/authorized_keys"
    echo ""
    read -p "Press Enter after adding the key to continue..."
fi

# Function to run commands on VPS
run_remote() {
    ssh -i ~/.ssh/seraphonix_deploy -o StrictHostKeyChecking=no $VPS_USER@$VPS_IP "$1"
}

# Function to copy files to VPS
copy_to_remote() {
    scp -i ~/.ssh/seraphonix_deploy -o StrictHostKeyChecking=no -r "$1" $VPS_USER@$VPS_IP:"$2"
}

echo "🚀 Starting deployment..."
echo ""

# Step 1: Prepare VPS
echo "📦 Step 1: Preparing VPS..."
run_remote "
    # Update system
    apt-get update -qq
    
    # Install Node.js if not present
    if ! command -v node &> /dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
        apt-get install -y nodejs
    fi
    
    # Install PM2 for process management
    if ! command -v pm2 &> /dev/null; then
        npm install -g pm2
    fi
    
    # Install Python for web server
    apt-get install -y python3
    
    echo 'VPS prepared successfully'
"
echo "✅ VPS prepared"
echo ""

# Step 2: Clean and create deployment directory
echo "🧹 Step 2: Setting up deployment directory..."
run_remote "
    # Stop existing processes
    pm2 stop seraphonix-api 2>/dev/null || true
    pm2 delete seraphonix-api 2>/dev/null || true
    pkill -f 'python3 -m http.server' 2>/dev/null || true
    
    # Clean and create directory
    rm -rf $DEPLOY_DIR
    mkdir -p $DEPLOY_DIR
"
echo "✅ Directory prepared"
echo ""

# Step 3: Copy files to VPS
echo "📤 Step 3: Copying files to VPS..."

# Copy backend
copy_to_remote "studio-saas/backend" "$DEPLOY_DIR/"

# Copy frontend
copy_to_remote "studio-saas/frontend" "$DEPLOY_DIR/"

echo "✅ Files copied"
echo ""

# Step 4: Install dependencies and start services
echo "⚙️  Step 4: Installing dependencies and starting services..."
run_remote "
    cd $DEPLOY_DIR/backend
    
    # Install dependencies
    npm install
    
    # Create data directories
    mkdir -p data streams
    
    # Set environment variables
    export PORT=$API_PORT
    export JWT_SECRET=\"seraphonix-studio-production-secret-$(date +%s)\"
    export NODE_ENV=production
    
    # Start API with PM2
    pm2 start server.js --name seraphonix-api -- \
        --port $API_PORT
    
    # Save PM2 config
    pm2 save
    
    # Setup PM2 startup
    pm2 startup systemd -u root --hp /root
    
    # Start web server
    cd $DEPLOY_DIR/frontend
    nohup python3 -m http.server $WEB_PORT > /dev/null 2>&1 &
    
    echo 'Services started'
"
echo "✅ Services started"
echo ""

# Step 5: Verify deployment
echo "🔍 Step 5: Verifying deployment..."
sleep 3

# Check API
API_STATUS=$(run_remote "curl -s -o /dev/null -w '%{http_code}' http://localhost:$API_PORT/api/health" || echo "000")
if [ "$API_STATUS" = "200" ]; then
    echo "✅ API is responding (HTTP $API_STATUS)"
else
    echo "⚠️  API check returned HTTP $API_STATUS"
fi

# Check Web
WEB_STATUS=$(run_remote "curl -s -o /dev/null -w '%{http_code}' http://localhost:$WEB_PORT" || echo "000")
if [ "$WEB_STATUS" = "200" ]; then
    echo "✅ Web server is responding (HTTP $WEB_STATUS)"
else
    echo "⚠️  Web check returned HTTP $WEB_STATUS"
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║           ✅ DEPLOYMENT COMPLETE                       ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║                                                        ║"
echo "║  🌐 Web Interface:  http://$VPS_IP                     ║"
echo "║  🔌 API Endpoint:   http://$VPS_IP:$API_PORT           ║"
echo "║                                                        ║"
echo "║  📊 Monitor:        pm2 status                         ║"
echo "║  📋 Logs:           pm2 logs seraphonix-api            ║"
echo "║                                                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "🎬 Seraphonix Studio is now live!"
echo ""
echo "Next steps:"
echo "  1. Visit http://$VPS_IP to access the platform"
echo "  2. Create an account or sign in"
echo "  3. Start your first broadcast!"
echo ""

# Save deployment info
DEPLOY_INFO="deployment-info.txt"
cat > $DEPLOY_INFO << EOF
Seraphonix Studio Deployment Info
==================================
Date: $(date)
VPS IP: $VPS_IP
Deploy Directory: $DEPLOY_DIR
API Port: $API_PORT
Web Port: $WEB_PORT

URLs:
- Web: http://$VPS_IP
- API: http://$VPS_IP:$API_PORT
- Health: http://$VPS_IP:$API_PORT/api/health

Management:
- View logs: ssh $VPS_USER@$VPS_IP "pm2 logs seraphonix-api"
- Restart: ssh $VPS_USER@$VPS_IP "pm2 restart seraphonix-api"
- Status: ssh $VPS_USER@$VPS_IP "pm2 status"

SSH Key: ~/.ssh/seraphonix_deploy
EOF

echo "💾 Deployment info saved to: $DEPLOY_INFO"
