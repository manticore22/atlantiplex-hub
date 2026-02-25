Hostinger VPS – Deployment Guide for Stripe Storefront + Lore CMS Gateway

Overview
- This guide describes how to deploy the Stripe storefront subdomain (stripe.verilysovereign.org) and gateway/lore CMS on a Hostinger VPS.
- Architecture:
  - Stripe storefront static assets served from /var/www/stripe by Nginx
  - Node.js backend for Stripe Checkout sessions and lore CMS at /var/www/vps-backend
  - Nginx proxies /create-checkout-session and /prices to the Node backend
  - Lore content served from the backend at /lore and /lore-content

Prerequisites
- A Hostinger VPS with Debian/Ubuntu Linux
- SSH access to the VPS
- Domain DNS configured:
  - A record: stripe.verilysovereign.org -> VPS_IP
  - A record: gateway.verilysovereign.org -> VPS_IP (if using gateway subdomain)
- TLS: Certbot access for TLS on both domains
- Node.js and npm available on VPS

What you’ll deploy
- Stripe storefront: stripe/index.html, stripe/shop-init.js, stripe/lore.html, stripe/studio.html, stripe/shop.html
- Gateway/landing: design-system-gateway files and gateway config (optional, can be added later)
- VPS backend: vps-backend/server.js, products.json, lore-content.json, subscriptions.json, etc.
- Nginx config: nginx-stripe.conf (example snippet)

Setup steps (high level)
1) Prepare directories
   - sudo mkdir -p /var/www/stripe
   - sudo mkdir -p /var/www/vps-backend
   - sudo mkdir -p /var/www/design-system
2) Copy files to server
   - Upload stripe/* to /var/www/stripe
   - Upload vps-backend/* to /var/www/vps-backend
   - Upload design-system/* (styles, tokens) if shared
3) Node backend
   - cd /var/www/vps-backend
   - npm install
   - Create a systemd service (vps-backend.service)
   - Set STRIPE_SECRET in environment or in a .env file
   - systemctl start vps-backend && systemctl enable vps-backend
4) Nginx config
   - Install Nginx
   - Put nginx-stripe.conf to /etc/nginx/sites-available/stripe.conf and link to sites-enabled
   - Ensure document roots point to /var/www/stripe for stripe.verilysovereign.org
   - TLS: certbot --nginx -d stripe.verilysovereign.org -d gateway.verilysovereign.org
   - Reload Nginx
5) Verify
   - Open https://stripe.verilysovereign.org/prices to see catalog
   - Use the storefront to start a checkout session or grant free access
6) Maintenance
   - Rotate Stripe keys; secure backend environment
   - Monitor logs: journalctl -u vps-backend -f, tail -f /var/log/nginx/access.log

Notes
- The free path is supported (no charge) for items flagged as free in products.json.
- For a production-ready system, replace file-based subscriptions.json with a real database and add robust auth, rate limiting, and webhook verification.
- For a single-tenant deployment, you can consolidate stripe.verilysovereign.org and gateway.verilysovereign.org behind a single Nginx server with virtual hosts.
