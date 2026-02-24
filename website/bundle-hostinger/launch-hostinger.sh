#!/usr/bin/env bash
set -euo pipefail

###############################
# Hostinger One-Domain Launch
# Gateway at root, Atlantiplex at /atlantiplex
###############################

DOMAIN=${1:-verilysovereign.org}
APP_ROOT="/opt/seraphinix"
ZIP_PATH="/home/$(whoami)/Seraphinix_Bundle_Hostinger_SaaS.zip"

LOG="/var/log/hostinger-launch.log"
exec > >(tee -a "$LOG") 2>&1

echo "[launch] Domain: $DOMAIN"
echo "[launch] App root: $APP_ROOT"
echo "[launch] Zip: $ZIP_PATH"

sudo apt update && sudo apt upgrade -y
sudo apt install -y nginx postgresql postgresql-contrib curl ufw certbot python3-certbot-nginx
curl -sL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2

echo "Setting up app directories..."
sudo mkdir -p "$APP_ROOT/apps/gateway"
sudo mkdir -p "$APP_ROOT/apps/atlantiplex-studio"
sudo mkdir -p "$APP_ROOT/apps/programs"
sudo mkdir -p "$APP_ROOT/design-system"

echo "Unzipping bundle..."
unzip -o "$ZIP_PATH" -d "$APP_ROOT" || { echo 'Bundle not found or unzip failed'; exit 1; }

echo "Installing dependencies..."
cd "$APP_ROOT/apps/gateway" && npm ci || npm install
cd "$APP_ROOT/apps/atlantiplex-studio" && npm ci || npm install

echo "Building apps..."
cd "$APP_ROOT/apps/gateway" && npm run build || true
cd "$APP_ROOT/apps/atlantiplex-studio" && npm run build || true

echo "Starting apps with PM2..."
pm2 delete gateway || true
pm2 delete atlantiplex || true
pm2 start --name gateway --prefix "$APP_ROOT/apps/gateway" npm -- start
pm2 start --name atlantiplex --prefix "$APP_ROOT/apps/atlantiplex-studio" npm -- start
pm2 save
pm2 startup systemd -u $(whoami) --hp /home/$(whoami)

echo "Configuring Nginx..."
sudo cp "$APP_ROOT/bundle-hostinger/nginx-seraphonix.conf" /etc/nginx/sites-available/seraphinix
sudo ln -sf /etc/nginx/sites-available/seraphinix /etc/nginx/sites-enabled/seraphinix
sudo nginx -t
sudo systemctl reload nginx

echo "Setting up TLS (Let’s Encrypt) for $DOMAIN..."
sudo certbot --nginx -d "$DOMAIN" -n --agree-tos --no-eff-mail
sudo systemctl reload nginx

echo "PostgreSQL bootstrap (example user/db) ..."
sudo -u postgres psql -c "CREATE USER saas_user WITH SUPERUSER CREATEDB CREATEROLE;" || true
sudo -u postgres psql -c "CREATE DATABASE saas_prod;" || true

echo "Deployment complete. Visit https://$DOMAIN"
