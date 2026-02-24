# Docker Quick Reference

## Start/Stop Services

```bash
# Development (with hot reload)
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml down

# Production
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml down

# View running services
docker compose ps
```

## Access Services

| Service | URL | Port | Purpose |
|---------|-----|------|---------|
| Frontend | http://localhost:5173 | 5173 | Vue/Vite UI |
| Stage API | http://localhost:9001 | 9001 | WebSocket & API |
| Flask API | http://localhost:5000 | 5000 | Backend Services |
| PostgreSQL | localhost:5432 | 5432 | Database |
| Redis | localhost:6379 | 6379 | Cache |
| Nginx | http://localhost | 80 | Reverse Proxy |

## View Logs

```bash
# All services
docker compose logs -f

# Specific service (last 100 lines)
docker compose logs --tail=100 -f stage-server

# Specific service, errors only
docker compose logs stage-server 2>&1 | grep ERROR

# Production logs
docker compose -f docker-compose.prod.yml logs -f
```

## Execute Commands

```bash
# Interactive shell
docker compose exec stage-server sh
docker compose exec flask-backend bash

# Database migration
docker compose exec flask-backend flask db upgrade

# Database query
docker compose exec postgres psql -U atlantiplex -d atlantiplex -c "SELECT 1;"

# Run npm command
docker compose exec stage-server npm ls
```

## Rebuild & Restart

```bash
# Rebuild all images
docker compose build

# Rebuild specific image
docker compose build stage-server

# Rebuild without cache
docker compose build --no-cache

# Restart service
docker compose restart stage-server
```

## Monitor Resources

```bash
# Real-time stats
docker stats

# Stats for all containers (formatted)
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# View container details
docker inspect atlantiplex-stage

# Check health status
docker inspect --format='{{.State.Health.Status}}' atlantiplex-stage
```

## Cleanup

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove all (unused)
docker system prune -a

# Remove with volumes (clean start)
docker compose down -v
```

## Development Workflow

### 1. Start Development Environment
```bash
docker compose -f docker-compose.dev.yml up -d
```

### 2. Edit Code (Hot Reload)
Edit files in:
- `matrix-studio/web/stage/` - Reloads automatically
- `matrix-studio/web/frontend/` - Reloads automatically
- `matrix-studio/` - Reloads automatically

### 3. View Changes
```bash
docker compose logs -f stage-server
```

### 4. Run Tests
```bash
docker compose exec stage-server npm test
docker compose exec flask-backend pytest
```

### 5. Database Migrations
```bash
docker compose exec flask-backend flask db upgrade
```

### 6. Stop Services
```bash
docker compose -f docker-compose.dev.yml down
```

## Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
# Database
DB_USER=atlantiplex
DB_PASSWORD=your-secure-password
DB_NAME=atlantiplex

# Cache
REDIS_PASSWORD=your-secure-password

# Authentication
JWT_SECRET=random-string-32-characters-minimum
JWT_REFRESH_SECRET=random-string-32-characters-minimum

# Payment
STRIPE_SECRET_KEY=sk_...
STRIPE_PUBLISHABLE_KEY=pk_...

# URLs
CORS_ORIGIN=http://localhost:5173
API_URL=http://localhost
```

## Troubleshooting

### Service won't start
```bash
docker compose logs stage-server
docker inspect atlantiplex-stage
```

### Port already in use
```bash
# Find process using port
lsof -i :5173

# Change port in docker-compose.yml or use different port
docker compose -f docker-compose.dev.yml -e "PORT=5174" up -d
```

### Database connection error
```bash
# Check PostgreSQL is running and healthy
docker compose exec postgres pg_isready

# Verify DATABASE_URL environment variable
docker compose exec stage-server env | grep DATABASE_URL
```

### Out of memory
```bash
# Check memory usage
docker stats

# Prune unused data
docker system prune -a --volumes
```

## File Structure

```
.
├── .dockerignore              # Build context optimization
├── .env.example               # Environment variables template
├── docker-compose.yml         # Default production compose
├── docker-compose.dev.yml     # Development with hot reload
├── docker-compose.prod.yml    # Production with resource limits
├── matrix-studio/
│   ├── Dockerfile.python      # Flask backend
│   ├── requirements.txt        # Python dependencies
│   └── web/
│       ├── stage/
│       │   ├── Dockerfile
│       │   ├── package.json
│       │   └── server.js
│       └── frontend/
│           ├── Dockerfile
│           ├── package.json
│           └── src/
└── nginx/
    ├── nginx.conf
    └── sites-enabled/
```

## Image Information

```bash
# View image details
docker images | grep atlantiplex

# Image size
docker image inspect atlantiplex-stage:latest \
  --format='{{.RepoTags}} - {{.Size}} bytes'

# Security scan
docker scout cves atlantiplex-stage:latest
```

## Common Errors

| Error | Solution |
|-------|----------|
| `connect ECONNREFUSED 127.0.0.1:5432` | PostgreSQL not running: `docker compose up -d postgres` |
| `Module not found` | Rebuild: `docker compose build --no-cache` |
| `Port 5173 already in use` | Stop other service: `lsof -i :5173` or change port |
| `health check timeout` | Service slow to start: check logs with `docker compose logs` |
| `OOM: Killed` | Out of memory: increase Docker memory or reduce `NODE_OPTIONS` |

## Quick Commands

```bash
# Copy for quick reference
docker compose ps
docker compose logs -f
docker compose exec stage-server sh
docker compose down
```

## Ports Reference

| Port | Service | Type |
|------|---------|------|
| 80 | Nginx | HTTP |
| 443 | Nginx | HTTPS |
| 5000 | Flask | API |
| 5173 | Frontend | Dev Server |
| 5432 | PostgreSQL | Database |
| 6379 | Redis | Cache |
| 9001 | Stage Server | WebSocket |

---

For detailed information, see [CONTAINERIZATION_GUIDE.md](./CONTAINERIZATION_GUIDE.md)
