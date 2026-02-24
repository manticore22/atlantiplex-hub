# Hostinger VPS One-Domain Patch (Gateway root, Atlantiplex under /atlantiplex)

Overview
- This patch is tailored to run Atlantiplex Studio as a two-app stack on a single Hostinger VPS domain: verilysovereign.org.
- Gateway landing is at / (root). Atlantiplex Studio is available at /atlantiplex.
- Includes: Nginx config, systemd/PM2 service definitions, SSL guidance, and a minimal SaaS core scaffold.

What you get in the patch
- gateway app (Next.js/Node) and Atlantiplex Studio app wired behind Nginx
- A design system (tokens) with tokens.css ready to be consumed by the apps
- A patch script to assemble and bundle the deployment assets
- Nginx site config for path-based routing
- Systemd/PM2 setup for keeping services alive
- PostgreSQL bootstrap script and a sample env for tenants
- Hostinger deployment guide (step-by-step)

How to deploy (high level)
- Prepare a VPS with Ubuntu 22.04, root access, and port 80/443 open
- Upload/patch: place the patch contents in a folder and run the setup script
- Run the bootstrap to install Node, Nginx, PostgreSQL, and PM2
- Start gateway and Atlantiplex services via PM2 and configure Nginx as a reverse proxy with TLS via certbot
- Verify by visiting verilysovereign.org

Notes
- This is a foundation for a single-domain hosting. We can later add a subdomain (e.g., atlantiplex.verilysovereign.org) if desired.
- For production you’ll want to connect to a real Stripe account and a persistent Postgres instance (Hostinger offers DB as a service or you can run locally).
