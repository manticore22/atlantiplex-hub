Deployment Bundle Overview

- This bundle contains everything needed to deploy the Stripe storefront + lore CMS gateway on a Hostinger VPS with a Stripe subdomain.
- Structure:
  - stripe/ (static storefront) - index.html, shop.html, shop-init.js, lore.html, studio.html
  - design-system/ (shared styles and tokens)
  - vps-backend/ (node backend for checkout + lore CMS)
  - nginx-stripe.conf (Nginx config for stripe.verilysovereign.org)
  - studio-website/ (landing + CTA + shop teaser)
  - HOSTINGER_DEPLOYMENT_GUIDE.md (existing)

How to deploy (summary)
- Prepare VPS: install Node.js, npm, Nginx, Certbot
- Create DNS A for stripe.verilysovereign.org to VPS IP
- Upload bundle contents to appropriate paths:
  - /var/www/stripe -> stripe/
  - /var/www/vps-backend -> vps-backend/
  - /var/www/design-system -> design-system/
- Install backend dependencies and start the Node server (systemd service)
- Configure Nginx to serve stripe.verilysovereign.org and proxy to the Node backend for /create-checkout-session and /prices
- Setup TLS with Certbot for stripe.verilysovereign.org
- Test endpoints and flow (free path and paid path)

Patch notes
- The bundle includes free-tier support by default; paid items require Stripe secrets in the backend environment.
- To extend, replace file-based storage with a proper DB and implement a login/auth flow.
