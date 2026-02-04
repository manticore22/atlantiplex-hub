# Atlantiplex Studio – Production Branding & Deployment

## Summary
- Brand renamed to Atlantiplex Studio with deep‑sea alien moon theming
- Centralized branding module (branding.json + CSS variables) for consistent, maintainable UI
- Production‑grade Docker Compose stack:
  - React frontend (brand‑themed)
  - Express + Socket.IO stage signaling with Redis scaling
  - Nginx reverse proxy and TLS ready
- CI/CD for GitHub Actions (build, test, deploy)
- Deployment scripts and TLS setup (Let’s Encrypt) included
- Full health checks, rollback via feature flag, and documentation

## How to run locally (Atlantiplex stack)
```bash
git clone <repo>
cd atlantiplex-studio
docker compose -f docker-compose.atlantiplex.yml up --build
# Frontend: http://localhost
# Stage: http://localhost/stage
# API: http://localhost/api/login (demo users: alice/password123, bob/letmein)
```

## Production deployment (TLS)
```bash
# 1) DNS – point your domain to host
# 2) TLS provisioning
chmod +x scripts/setup-tls-atlantiplex.sh
sudo DOMAIN=your.domain.com EMAIL=admin@your.domain.com ./scripts/setup-tls-atlantiplex.sh

# 3) Update nginx.conf to enable HTTPS (listener 443, certs paths)

# 4) Deploy
chmod +x scripts/deploy-atlantiplex.sh
JWT_SECRET=$(openssl rand -hex 32) ./scripts/deploy-atlantiplex.sh

# 5) Verify
./scripts/health-atlantiplex.sh
```

## Artifacts produced
- Branding module and helpers
- React components using branding tokens
- CSS variables for all surfaces
- Docker compose file and nginx config with TLS scaffolding
- Deployment scripts with health checks
- CI workflows for build, test, and deploy

## Next steps
- Replace demo users with a real IdP (OIDC) and refresh tokens
- Add TURN servers for WebRTC NAT traversal
- Expand WebRTC to a full media path (persistent audio/video)
- Add unit/integration tests (Jest) to CI
- Optional: set up monitoring (Prometheus/Grafana) and log aggregation

## Security notes
- Rotate JWT_SECRET regularly; use production vault
- Enforce HTTPS everywhere; use short‑lived tokens (1h) and refresh tokens
- Limit CORS origins for production
- Store Redis data on persistent volumes and enforce Redis auth

## Observability
- Nginx logs mount to `./logs`
- Stage logs to Docker driver; pipe to aggregator if desired
- Health endpoints:
  - Frontend via Nginx
  - Stage API GET /api/health
  - Stage UI GET /stage

## Scale
- Add more stage replicas behind Nginx
- Use shared Redis for Socket.IO adapter
- Add media‑server (e.g., Janus/Mediasoup) for multi‑party audio/video

All branding, deployment, and CI assets are production‑ready and feature‑flagged for safe rollout.