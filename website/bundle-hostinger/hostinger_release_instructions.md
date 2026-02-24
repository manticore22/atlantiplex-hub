Hostinger One-Domain Patch – Quick Deployment Guide

Overview
- This guide describes a one-domain deployment (gateway at root, Atlantiplex at /atlantiplex) on Hostinger VPS.
- You will deploy using the Seraphinix_Bundle_Hostinger_SaaS.zip patch.

Prereqs
- A Hostinger VPS running Ubuntu 22.04 LTS with root access
- Domain verilysovereign.org pointing to the VPS IP
- Docker or Docker Compose installed (we’ll use Docker in this patch for clarity, but you can adapt to PM2 + Nginx if you prefer)

What you will deploy
- gateway app (Next.js/Node) at root
- atlantiplex-studio app at /atlantiplex
- Nginx reverse proxy config for root and /atlantiplex
- PostgreSQL DB bootstrap
- TLS via Let’s Encrypt
- A small SaaS core scaffold for tenancy and billing stubs
- A one-click launcher script (launch-hostinger.sh)

One-click patch usage (step-by-step)

If you want, I can trigger the final ZIP build here and return a direct download link or attach the file to a chat message, whichever you prefer.
