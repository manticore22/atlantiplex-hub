# Quick Start Guide - Atlantiplex Studio Docker Setup

## Prerequisites

- Docker 20.10+ installed
- Docker Compose 2.0+ installed
- 4GB RAM minimum (8GB+ recommended)
- 20GB free disk space

## Quick Start (5 minutes)

### 1. Clone or navigate to project directory
```bash
cd atlantiplex-hub
```

### 2. Create environment file
```bash
cp .env.example .env
```

Edit `.env` with your secrets:
```env
DB_PASSWORD=your-secure-password-123
JWT_SECRET=your-jwt-secret-key
REDIS_PASSWORD=your-redis-password
STRIPE_SECRET_KEY=sk_your_stripe_key
```

### 3. Build frontend assets
```bash
docker compose --profile build up -d frontend-builder
docker compose logs -f frontend-builder
```

Wait for the build to complete (you'll see "Built in ... ms")

### 4. Start all services
```bash
docker compose up -d
```

### 5. Verify services are healthy
```bash
docker compose ps
```

Expected output:
```
NAME                          STATUS
atlantiplex-postgres          Up (healthy)
atlantiplex-redis             Up (healthy)
atlantiplex-stage             Up (healthy)
atlantiplex-flask             Up (healthy)
atlantiplex-nginx             Up (healthy)
```

### 6. Access the application
- Frontend: `http://localhost`
- Stage Server API: `http://localhost:9001`
- Flask Backend API: `http://localhost:5000`

## Troubleshooting

### Containers not starting?
```bash
# Check logs for specific service
docker compose logs stage-server
docker compose logs flask-backend

# Restart services
docker compose restart
```

### Port conflicts?
Update docker-compose.yml port mappings or stop conflicting services:
```bash
# Find process using port 80
lsof -i :80  # macOS/Linux
netstat -ano | findstr :80  # Windows
```

### Database connection errors?
```bash
# Wait for postgres to be healthy
docker compose exec postgres pg_isready -U atlantiplex

# Check Redis connectivity
docker compose exec redis redis-cli ping
```

### Out of disk space?
```bash
# Clean up dangling images and volumes
docker system prune -a
docker volume prune
```

## Common Commands

```bash
# View logs
docker compose logs -f              # All services
docker compose logs -f flask-backend # Specific service
docker compose logs --tail 50       # Last 50 lines

# Execute commands
docker compose exec flask-backend bash
docker compose exec postgres psql -U atlantiplex

# Restart services
docker compose restart              # All services
docker compose restart stage-server # Specific service

# Stop without removing
docker compose stop

# Stop and remove containers (keeps volumes)
docker compose down

# Remove everything including volumes (caution!)
docker compose down -v

# Rebuild without cache
docker compose build --no-cache

# Update specific service
docker compose up -d --no-deps --build stage-server
```

## Development Workflow

### Local development with hot reload

1. Modify source code
2. For frontend changes:
   ```bash
   docker compose exec stage-server npm run build:frontend
   ```

3. For backend changes:
   ```bash
   # Python changes auto-reload with Flask
   # Node.js changes require restart
   docker compose restart flask-backend
   docker compose restart stage-server
   ```

## Production Deployment

### Before going live:

1. **Change all secrets in `.env`**
   - Generate strong passwords
   - Use secure random strings for JWT secrets

2. **Update Nginx configuration**
   - Enable SSL/TLS in `./nginx/nginx.conf`
   - Update domain names

3. **Database backup**
   ```bash
   docker compose exec postgres pg_dump -U atlantiplex atlantiplex > backup.sql
   ```

4. **Check resource limits**
   - Add memory limits to docker-compose.yml
   - Monitor CPU/memory usage

5. **Enable logging**
   - Configure log rotation
   - Send logs to centralized logging service

### Deploy to server:

```bash
# SSH to server
ssh user@production-server

# Clone repository
git clone <your-repo-url>
cd atlantiplex-hub

# Set production environment
export DB_PASSWORD=production-password
export JWT_SECRET=production-jwt-secret

# Build images
docker compose build

# Start services
docker compose up -d

# Verify
docker compose ps
docker compose logs -f
```

## Monitoring

### Health check status
```bash
docker compose ps --format "table {{.Names}}\t{{.Status}}"
```

### Resource usage
```bash
docker stats
```

### Check service logs
```bash
docker compose logs -f flask-backend --tail 100
```

## Backup & Recovery

### Backup database
```bash
docker compose exec postgres pg_dump -U atlantiplex atlantiplex > atlantiplex_backup.sql
```

### Restore database
```bash
docker compose exec -T postgres psql -U atlantiplex atlantiplex < atlantiplex_backup.sql
```

### Backup volumes
```bash
# Backup uploads
docker run --rm -v atlantiplex-hub_stage_uploads:/data -v $(pwd):/backup ubuntu tar czf /backup/uploads.tar.gz -C /data .
```

## Support & Documentation

For detailed information, see:
- `DOCKER_BEST_PRACTICES.md` - Security and optimization details
- `docker-compose.yml` - Service configuration
- `./matrix-studio/*/Dockerfile` - Image build instructions

## Next Steps

1. ✅ Verify all services are running
2. ✅ Test login functionality
3. ✅ Configure payment processing
4. ✅ Set up SSL/TLS certificates
5. ✅ Configure backup procedures
6. ✅ Plan monitoring and alerting
