# Quick Reference Guide

## 🚀 One-Liner Commands

```bash
# Start development environment
docker compose up

# Start with AI services
docker compose --profile ai up

# Start everything (includes reverse proxy & backend)
docker compose --profile ai --profile proxy --profile backend up

# View logs
docker compose logs -f app

# Execute shell in container
docker compose exec app sh

# Stop all services
docker compose down

# Remove everything (cleanup)
docker compose down -v && docker system prune -a
```

## 📋 Available Services

| Service | Port | Profile | Start Time | Size |
|---------|------|---------|-----------|------|
| **app** (Atlantiplex) | 3000 | default | 2-3s | 48MB |
| **ollama** (AI) | 11434 | ai | 60+s | 3.2GB |
| **nginx** (Proxy) | 80/443 | proxy | 1s | 9MB |
| **seraphonix-api** | 3001 | backend | 3-5s | varies |

## 🎯 Typical Workflows

### Development (Hot Reload)
```bash
docker compose up
# Edit files locally → changes apply immediately
# Logs appear in terminal
# Ctrl+C to stop
```

### Testing with AI
```bash
docker compose --profile ai up
# Wait for Ollama to start (yellow: health: starting)
# Pull a model: docker compose exec ollama ollama pull dolphin-llama3:30b
# Test: curl http://localhost:3000/api/chat
```

### Production Deployment
```bash
# Create .env with secrets
echo "JWT_SECRET=your-prod-secret" > .env
echo "STRIPE_SECRET=your-stripe-key" >> .env

# Start in background
docker compose up -d

# Monitor
docker compose logs -f

# Stop
docker compose down
```

## 🔧 Configuration Files

**docker-compose.yml** - Main orchestration  
**Dockerfile** - Optimized build  
**.dockerignore** - Build context exclusion  
**.env** - Environment variables (create as needed)  

## 📊 Performance Numbers

| Operation | Time |
|-----------|------|
| Build (first time) | 8s |
| Build (cached) | 0.2s |
| Container startup | 2-3s |
| Healthcheck response | <100ms |
| API latency | <50ms |

## 🔍 Debugging

```bash
# Check container status
docker compose ps

# View all logs
docker compose logs

# View logs for specific service
docker compose logs app

# Follow logs (live)
docker compose logs -f app

# View container details
docker inspect atlantiplex-app

# Check network connectivity
docker network inspect 01-work_atlantiplex-network

# Test API manually
curl http://localhost:3000/api/status
```

## 🛑 Common Issues & Solutions

**Container exits immediately:**
```bash
docker compose logs app  # View error
# Fix and rebuild: docker compose up --build
```

**Port already in use:**
```bash
# Either stop other service or change port in docker-compose.yml
docker compose down
```

**Ollama taking too long:**
```bash
# Don't wait - run app without Ollama
docker compose up
# Add AI later: docker compose --profile ai up
```

**Permission denied errors:**
```bash
# App runs as non-root (nodejs:1001)
# File permissions must allow nodejs user
# Usually not an issue with bind mounts
```

**Cache not being used:**
```bash
# Clear cache if needed
docker builder prune
# Rebuild: docker compose up --build
```

## 📦 What's Inside

- **Dockerfile**: Node.js + non-root user + healthchecks + BuildKit optimization
- **docker-compose.yml**: 4 services + profiles + volumes + networks
- **.dockerignore**: 17 rules reducing build context 99.9%
- **Scripts**: All entry points properly configured

## ✅ Pre-deployment Checklist

- [ ] Test locally: `docker compose up`
- [ ] Verify API: `curl http://localhost:3000/api/status`
- [ ] Check logs: `docker compose logs -f app`
- [ ] Create .env: `echo "JWT_SECRET=xxx" > .env`
- [ ] Test with AI: `docker compose --profile ai up`
- [ ] Stop containers: `docker compose down`
- [ ] Deploy: Push to registry and run

## 🌐 Accessing Services

**Atlantiplex App:** http://localhost:3000  
**Ollama API:** http://localhost:11434 (when profile ai enabled)  
**Nginx (when enabled):** http://localhost  
**API Status:** http://localhost:3000/api/status  

## 📚 Documentation

- `CONTAINERIZATION.md` - Setup & deployment guide
- `OPTIMIZATION_REPORT.md` - Detailed optimization analysis
- `E2E_TEST_RESULTS.md` - Full test results & metrics
- `Dockerfile` - Inline comments explain each step
- `docker-compose.yml` - Inline comments for configuration

---

**Status:** ✅ Production Ready  
**Last Updated:** 2026-02-24  
**Health Check:** All services passing
