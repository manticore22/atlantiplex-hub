VPS Backend for Verily Sovereign Stripe Gateways

- Provides a minimal Express server to handle Stripe Checkout sessions and render lore from JSON.
- Intended to run behind a reverse proxy (Nginx) on Hostinger VPS, with subdomains:
- stripe.verilysovereign.org -> Stripe storefront (Checkout sessions)
- gateway.verilysovereign.org -> gateway to design-system playground and lore CMS

Prerequisites
- Node.js installed on VPS
- Stripe account with API keys
- Nginx configured with DNS to verilysovereign.org and subdomains

Usage
- Install: npm install
- Run: npm start (or set up as systemd service)
- Environment: set STRIPE_SECRET to your Stripe secret key

Notes
- This is a minimal starter. We can expand to a full CMS, more routes, and secure webhooks as needed.
