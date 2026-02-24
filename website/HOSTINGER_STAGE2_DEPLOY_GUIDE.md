Stage 2 Deployment Guide (Atlantiplex Studio)

Goal: Bring Atlantiplex Studio online at verilysovereign.org/atlantiplex with Stage 1 gateway already deployed.

Prerequisites:
- DNS set for verilysovereign.org (A records pointing to your VPS)
- TLS certificates (Let’s Encrypt) configured for verilysovereign.org
- Docker & Docker Compose installed on the VPS

1) Prepare Stage 2 files
- Copy docker-compose.stage2.yml to the server and place next to docker-compose.stage1.yml
- Copy nginx-stage2.conf to /etc/nginx/nginx.stage2.conf and ensure paths match
- Copy verilysovereign-backend scaffolding (server.js, data/ ) to the server
- Copy Atlantiplex Studio image/build context to the server if needed

2) Start Stage 2 services
- docker-compose -f docker-compose.stage2.yml up -d --build
- Check containers: docker ps

3) Nginx routing
- Ensure nginx.stage2.conf handles /atlantiplex/ routing to atlantiplex container
- Reload Nginx: sudo nginx -s reload

4) TLS
- Optional: point TLS for verilysovereign.org to stage 2 config; ensure certs valid for the domain

5) Verify
- Access https://verilysovereign.org/atlantiplex/
- Check /health and admin metrics endpoint if admin is enabled

6) Finalize
- Document how to push updates to Stage 2 via docker-compose
- Add health checks for Stage 2 readiness in your monitoring system

That's the high-level flow. I can tailor this into a script you can run in one shot.
