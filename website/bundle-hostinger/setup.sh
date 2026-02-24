#!/usr/bin/env bash
set -euo pipefail

echo "Hostinger one-domain setup bootstrap"
echo "Updating system..."
sudo apt update && sudo apt upgrade -y

echo "Installing dependencies (nginx, postgresql, node, npm, certbot)…"
sudo apt install -y nginx postgresql postgresql-contrib curl ufw certbot python3-certbot-nginx
curl -sL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2

echo "Creating app directory structure..."
sudo mkdir -p /opt/seraphinix/apps/gateway
sudo mkdir -p /opt/seraphinix/apps/atlantiplex-studio
sudo mkdir -p /opt/seraphinix/apps/programs
sudo mkdir -p /opt/seraphinix/design-system

echo "Patching in code is expected to be done prior to running this script. This script prepares the host and dependencies."

echo "Setting up Nginx TLS and reverse proxy (manual steps continue below)."
echo "Install complete. Run npm install in both app dirs and start with PM2." 
