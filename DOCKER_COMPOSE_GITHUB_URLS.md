# Docker Compose URLs - GitHub Repository

## Repository Information

**Repository URL:** https://github.com/manticore22/atlantiplex-hub
**Main Branch:** https://github.com/manticore22/atlantiplex-hub/tree/main
**Release Tag:** v1.0.0-production-ready

---

## Docker Compose Files

### Production Environment
- **Browser View:** https://github.com/manticore22/atlantiplex-hub/blob/main/docker-compose.prod.yml
- **Raw Download:** https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml
- **Use:** `docker-compose -f docker-compose.prod.yml up`

### Development Environment
- **Browser View:** https://github.com/manticore22/atlantiplex-hub/blob/main/docker-compose.dev.yml
- **Raw Download:** https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.dev.yml
- **Use:** `docker-compose -f docker-compose.dev.yml up`

### Main (Default)
- **Browser View:** https://github.com/manticore22/atlantiplex-hub/blob/main/docker-compose.yml
- **Raw Download:** https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.yml
- **Use:** `docker-compose up`

### Testing Environment
- **Browser View:** https://github.com/manticore22/atlantiplex-hub/blob/main/docker-compose.test.yml
- **Raw Download:** https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.test.yml

### Hub Environment
- **Browser View:** https://github.com/manticore22/atlantiplex-hub/blob/main/docker-compose.hub.yml
- **Raw Download:** https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.hub.yml

---

## Quick Start Commands

### Clone and Run (Recommended)
```bash
git clone https://github.com/manticore22/atlantiplex-hub.git
cd atlantiplex-hub
git checkout main
docker-compose -f docker-compose.prod.yml up
```

### Run Without Cloning
```bash
# Download specific compose file
curl -o docker-compose.prod.yml https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml

# Run it
docker-compose -f docker-compose.prod.yml up
```

### Using Docker Compose from URL (if supported by your version)
```bash
docker-compose -f https://raw.githubusercontent.com/manticore22/atlantiplex-hub/main/docker-compose.prod.yml up
```

---

## Kubernetes Deployment Files

If you prefer Kubernetes instead of Docker Compose:

**Kubernetes Manifests Directory:**
https://github.com/manticore22/atlantiplex-hub/tree/main/k8s

**Deployment Guide:**
https://github.com/manticore22/atlantiplex-hub/blob/main/KUBERNETES_DEPLOYMENT_GUIDE.md

**Deployment Script:**
https://github.com/manticore22/atlantiplex-hub/blob/main/deploy-to-k8s-and-github.ps1

---

## Key Files in Repository

| File | URL |
|------|-----|
| docker-compose.prod.yml | https://github.com/manticore22/atlantiplex-hub/blob/main/docker-compose.prod.yml |
| docker-compose.dev.yml | https://github.com/manticore22/atlantiplex-hub/blob/main/docker-compose.dev.yml |
| DEPLOYMENT_PACKAGE_INDEX.md | https://github.com/manticore22/atlantiplex-hub/blob/main/DEPLOYMENT_PACKAGE_INDEX.md |
| KUBERNETES_DEPLOYMENT_GUIDE.md | https://github.com/manticore22/atlantiplex-hub/blob/main/KUBERNETES_DEPLOYMENT_GUIDE.md |
| deploy-to-k8s-and-github.ps1 | https://github.com/manticore22/atlantiplex-hub/blob/main/deploy-to-k8s-and-github.ps1 |
| k8s/ (all manifests) | https://github.com/manticore22/atlantiplex-hub/tree/main/k8s |

---

## What to Do With These URLs

### Option 1: Browser View (Best for Reading)
Click any "Browser View" URL to read the file on GitHub

### Option 2: Raw Download (Best for Using)
- Use "Raw Download" URLs in scripts or CI/CD pipelines
- Example: `curl -o file.yml https://raw.githubusercontent.com/...`

### Option 3: Clone Repository (Best for Full Project)
```bash
git clone https://github.com/manticore22/atlantiplex-hub.git
cd atlantiplex-hub
```

---

## Troubleshooting the Build Error

If you see "No Docker compose files found" error:

1. **Make sure you're on the main branch:**
   ```bash
   git checkout main
   ```

2. **Verify files exist:**
   ```bash
   ls -la docker-compose*.yml
   ```

3. **List all files in repo:**
   ```bash
   git ls-files | grep docker-compose
   ```

4. **Pull latest:**
   ```bash
   git pull origin main
   ```

---

## Environment Variables

Before running Docker Compose, create a `.env` file:

```bash
# Copy the template
cp .env.example .env

# Edit with your values
nano .env  # or your preferred editor
```

**Key variables to set:**
- `DB_PASSWORD` - PostgreSQL password
- `REDIS_PASSWORD` - Redis password
- `JWT_SECRET` - API authentication secret
- `STRIPE_SECRET_KEY` - Stripe payment key
- `CORS_ORIGIN` - Your domain

---

## Services Included

With Docker Compose you get:

- **nginx** - Reverse proxy + load balancer
- **PostgreSQL** - Database (50GB)
- **Redis** - Cache/session store
- **Stage-Server** - Node.js API (2 replicas)
- **Flask-Backend** - Python AI backend (2 replicas)
- **Frontend** - React SPA (nginx)
- **Gateway** - API router
- **Website** - Static content

---

## Docker Compose Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove volumes
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# View running services
docker-compose ps
```

---

## Status

✅ All Docker Compose files are in GitHub
✅ Repository is on main branch
✅ All configurations are committed
✅ Ready to use

**Repository:** https://github.com/manticore22/atlantiplex-hub
**Branch:** main
**Status:** Production Ready
