# Atlantiplex Studio - Docker Containerization Guide

## Overview

Your Atlantiplex Studio project has been fully containerized following Docker's best practices. This guide explains the setup, usage, and deployment strategies.

## Architecture

The application uses a multi-container setup with:

- **PostgreSQL 15** - Primary database
- **Redis 7** - Cache & session storage
- **Node.js 20 (Stage Server)** - WebSocket API on port 9001
- **Python 3.11 (Flask)** - Backend services on port 5000
- **Frontend (Vue/Vite)** - Built static files, served via Nginx on port 5173
- **Nginx 1.25** - Reverse proxy & load balancer on ports 80/443

## Files Structure

```
.
├── .dockerignore                    # Optimized build context
├── docker-compose.yml               # Production Compose file (recommended)
├── docker-compose.dev.yml           # Development Compose file (with hot reload)
├── docker-compose.prod.yml          # Production with resource limits
├── matrix-studio/
│   ├── Dockerfile.python            # Flask backend (multi-stage)
│   ├── requirements.txt              # Python dependencies
│   └── web/
│       ├── stage/
│       │   └── Dockerfile           # Node.js Stage Server
│       └── frontend/
│           └── Dockerfile           # Vue/Vite frontend (multi-stage)
└── nginx/
    ├── nginx.conf                   # Nginx configuration
    └── sites-enabled/               # Site configs
```

## Dockerfile Best Practices Used

### Multi-Stage Builds
- **Python**: Separate builder and runtime stages to minimize image size
- **Frontend**: Build assets in builder stage, serve from minimal Nginx runtime
- **Node.js**: Optimized for minimal footprint while maintaining security

### Security Hardening
- ✅ Non-root user execution (nodejs:1001, appuser:1001, nginx:101)
- ✅ Dropped unnecessary capabilities (`cap_drop: ALL` + selective `cap_add`)
- ✅ No new privileges flag (`security_opt: no-new-privileges:true`)
- ✅ Dumb-init for proper signal handling (PID 1 problem)
- ✅ Read-only root filesystem for Nginx (tmpfs mounts for /var/run, /var/cache)
- ✅ Health checks on all services
- ✅ Minimal base images (Alpine Linux)

### Performance Optimization
- ✅ Layer caching - Dockerfile instructions ordered for maximum cache hits
- ✅ Multi-stage builds - Reduced final image sizes
- ✅ `.dockerignore` - Optimized build context (excludes: node_modules, logs, docs, etc.)
- ✅ `npm ci` instead of `npm install` - Faster, deterministic builds
- ✅ Cache cleaning - `npm cache clean --force` and `pip --no-cache-dir`

## Quick Start

### Prerequisites
- Docker Desktop or Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ RAM for local development

### Development Environment

Build and start all services for local development:

```bash
# Copy environment file (adjust variables as needed)
cp .env.example .env

# Start development stack with hot reload
docker compose -f docker-compose.dev.yml up -d

# View logs
docker compose -f docker-compose.dev.yml logs -f

# Access services
# Frontend: http://localhost:5173
# Stage API: http://localhost:9001
# Flask API: http://localhost:5000
# Nginx (optional): http://localhost
```

### Production Environment

Prepare production environment:

```bash
# Copy and configure production environment
cp .env.example .env.production
# Edit .env.production with production values:
# - Strong DB_PASSWORD
# - Strong REDIS_PASSWORD
# - Proper JWT_SECRET and JWT_REFRESH_SECRET
# - Real Stripe keys
# - Production CORS_ORIGIN
# - Production API_URL

# Build frontend static files (one-time)
docker compose -f docker-compose.prod.yml --profile build up frontend-builder

# Start production stack
docker compose -f docker-compose.prod.yml -f .env.production up -d

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

## Environment Configuration

### Required Environment Variables

See `.env.example` for all options. Minimum required for production:

```bash
# Database
DB_USER=atlantiplex
DB_PASSWORD=<STRONG_PASSWORD>
DB_NAME=atlantiplex

# Redis
REDIS_PASSWORD=<STRONG_PASSWORD>

# JWT
JWT_SECRET=<RANDOM_32+_CHAR_STRING>
JWT_REFRESH_SECRET=<RANDOM_32+_CHAR_STRING>

# Stripe
STRIPE_SECRET_KEY=sk_...
STRIPE_PUBLISHABLE_KEY=pk_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Application
CORS_ORIGIN=https://yourdomain.com
API_URL=https://yourdomain.com
NODE_ENV=production
FLASK_ENV=production
```

## Deployment

### Local Testing (Production-like)

Test with production compose file:

```bash
# Start with production config (locally)
docker compose -f docker-compose.prod.yml --env-file .env up -d

# Monitor health checks
docker compose -f docker-compose.prod.yml ps
```

### Docker Stack Deploy (Swarm)

For Docker Swarm:

```bash
# Initialize swarm (if not already)
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml atlantiplex

# View status
docker service ls
docker service logs atlantiplex_stage-server
```

### Kubernetes Deployment

Recommended for larger deployments. See separate Kubernetes documentation.

## Compose Files Explained

### docker-compose.yml (Default - Production)
- Security-hardened configuration
- Health checks on all services
- Resource limits
- Proper restart policies
- Suitable for production single-host deployments

### docker-compose.dev.yml (Development)
- Hot reload via volume mounts
- Exposed ports for direct service access
- Debug logging enabled
- Relaxed security (dev only)
- Optional Nginx profile for testing

### docker-compose.prod.yml (Production Advanced)
- Resource limits and reservations
- Replicas configuration
- Advanced logging with rotation
- Explicit environment validation
- Optimized for larger deployments

## Health Checks

All services include health checks:

```bash
# View health status
docker compose ps

# Check specific service health
docker compose exec postgres pg_isready

# View health check logs
docker inspect --format='{{json .State.Health.Log}}' atlantiplex-postgres | jq .
```

## Logs & Monitoring

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f stage-server
docker compose logs -f flask-backend

# Follow only errors
docker compose logs -f --tail=50 | grep ERROR

# View logs for production
docker compose -f docker-compose.prod.yml logs -f
```

## Performance Tuning

### Database (PostgreSQL)
- Adjust `POSTGRES_INITDB_ARGS` for specific workloads
- Volume mounted to `/data/atlantiplex/postgres` for persistence

### Cache (Redis)
- `maxmemory`: Set based on available RAM (current: 512MB for prod, 256MB for dev)
- `maxmemory-policy`: `allkeys-lru` evicts least-used keys when full
- AOF persistence enabled for durability

### Node.js Services
- `NODE_OPTIONS: --max-old-space-size=512`: Heap size limit (adjust for workload)
- Health check configured with 40s start period for initialization

### Python Flask
- Production WSGI server recommended for prod (currently using Flask dev server)
- Consider Gunicorn: `CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "4", "app:app"]`

### Nginx
- `worker_processes: auto` - Uses available CPU cores
- Gzip compression enabled
- Static asset caching headers optimized
- tmpfs for cache and logs (no disk I/O)

## Common Tasks

### Stop Services
```bash
docker compose down
```

### Remove Volumes (Clean Start)
```bash
docker compose down -v
```

### Rebuild Images
```bash
docker compose build --no-cache
```

### Execute Commands in Container
```bash
# Database migration
docker compose exec flask-backend flask db upgrade

# Restart service
docker compose restart stage-server

# Interactive shell
docker compose exec stage-server sh
```

### View Resource Usage
```bash
docker stats

# Pretty format
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Clean Up Unused Resources
```bash
# Remove stopped containers, unused images, build cache
docker system prune -a

# Reclaim disk space
docker system prune -a --volumes
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker compose logs stage-server

# Check health status
docker compose ps stage-server

# Inspect container details
docker inspect atlantiplex-stage

# Test connectivity
docker compose exec nginx wget -v http://stage-server:9001/health
```

### Database Connection Failed

```bash
# Check PostgreSQL health
docker compose exec postgres pg_isready

# Test connection string
docker compose exec stage-server psql "$DATABASE_URL" -c "SELECT 1;"
```

### High Memory Usage

```bash
# Check memory stats
docker stats --no-stream

# Adjust limits in docker-compose.prod.yml:
# services:
#   stage-server:
#     deploy:
#       resources:
#         limits:
#           memory: 2G
#         reservations:
#           memory: 1G
```

### Port Conflicts

If ports are already in use:

```bash
# Find process using port
lsof -i :80  # macOS/Linux
netstat -ano | findstr :80  # Windows

# Or use different ports in docker-compose override
# services:
#   nginx:
#     ports:
#       - "8080:80"  # Map to different port
```

## Scaling

### Horizontal Scaling (Multiple Instances)

For Swarm/Kubernetes:

```bash
# Scale Node.js service to 3 replicas
docker service scale atlantiplex_stage-server=3

# In docker-compose.prod.yml (manual):
# services:
#   stage-server:
#     deploy:
#       replicas: 3
```

### Load Balancing

Nginx upstream already configured for multiple backends:

```nginx
upstream stage_server {
    server stage-server:9001;  # Add more: server stage-server-2:9001;
}
```

## Image Registry

### Build and Push to Docker Hub

```bash
# Build images
docker compose build

# Tag for registry
docker tag atlantiplex-stage:latest myregistry/atlantiplex-stage:latest

# Push
docker push myregistry/atlantiplex-stage:latest

# Pull from registry
docker pull myregistry/atlantiplex-stage:latest

# Update compose to use registry
# image: myregistry/atlantiplex-stage:latest
```

## Security Checklist

- ✅ Non-root users in all containers
- ✅ Capabilities dropped (no-new-privileges)
- ✅ Health checks enabled
- ✅ .env file in .gitignore (use strong secrets)
- ✅ Secrets not hardcoded in Dockerfiles
- ✅ Alpine base images (minimal attack surface)
- ✅ Dumb-init for signal handling
- ✅ Read-only filesystems where possible
- ✅ HTTPS configured in Nginx (SSL certs in ./nginx/ssl/)
- ✅ Resource limits set (prevent DoS)

### Additional Security Measures

1. **Network isolation**: Use dedicated network bridge
2. **Secret management**: Use Docker secrets in Swarm or external secret managers
3. **Image scanning**: `docker scout cves atlantiplex-stage:latest`
4. **Audit logs**: Configure Docker daemon logging
5. **HTTPS/TLS**: Configure certificates in Nginx

## Maintenance

### Backup

```bash
# Backup database
docker compose exec postgres pg_dump -U atlantiplex -d atlantiplex > backup.sql

# Backup Redis
docker compose exec redis redis-cli BGSAVE

# Backup volumes
docker run --rm -v atlantiplex_postgres_data:/data -v $(pwd):/backup \
    alpine tar czf /backup/postgres-backup.tar.gz -C /data .
```

### Restore

```bash
# Restore database
docker compose exec -T postgres psql -U atlantiplex -d atlantiplex < backup.sql

# Restore Redis
docker compose exec redis redis-cli BGREWRITEAOF
```

### Updates

```bash
# Update base images
docker pull postgres:15-alpine
docker pull node:20-alpine
docker pull python:3.11-alpine
docker pull nginx:1.25-alpine

# Rebuild with updated bases
docker compose build --no-cache

# Restart services
docker compose up -d
```

## Additional Resources

- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)

## Support

For issues or questions:
1. Check logs: `docker compose logs -f`
2. Check health: `docker compose ps`
3. Review configuration: `docker inspect <container>`
4. Test connectivity: `docker compose exec <service> wget <endpoint>`

---

**Last Updated**: 2024
**Docker Version**: 20.10+ recommended
**Docker Compose Version**: 2.0+ recommended
