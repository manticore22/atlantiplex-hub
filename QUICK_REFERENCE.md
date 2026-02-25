# Quick Reference: Atlantiplex Studio Docker Stack

## Verify Everything Works

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status (all should be healthy)
docker-compose ps

# Test endpoints
curl http://localhost:9001/health
curl http://localhost:5000/api/health
```

## Vulnerability Check

```bash
# Scan all images for CVEs
docker scout cves atlantiplex-stage:latest
docker scout cves atlantiplex-flask:latest
docker scout cves atlantiplex-frontend:latest
```

## View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker logs -f atlantiplex-stage
docker logs -f atlantiplex-flask
docker logs -f atlantiplex-postgres
```

## Stop Everything

```bash
docker-compose down
```

## Development

```bash
# Rebuild without cache (useful after updates)
docker-compose build --no-cache

# Rebuild one service
docker-compose build stage-server

# Start in foreground (see logs in real-time)
docker-compose up
```

## Database Access

```bash
# Connect to PostgreSQL
docker exec -it atlantiplex-postgres psql -U atlantiplex -d atlantiplex

# Connect to Redis
docker exec -it atlantiplex-redis redis-cli -a ${REDIS_PASSWORD}
```

## Key Metrics

- **Build time**: ~60s (first), ~10s (code changes)
- **Startup time**: ~60s to fully healthy
- **Image sizes**: Node 48MB, Flask 24MB, Nginx ~44MB
- **Vulnerabilities**: 5 remaining (4 are build-time tools)
- **Security**: Non-root users, multi-stage, Alpine base

## Important Files

- `docker-compose.yml` - Production configuration
- `docker-compose.test.yml` - Test configuration
- `./matrix-studio/web/stage/Dockerfile` - Node.js
- `./matrix-studio/web/frontend/Dockerfile` - React
- `./matrix-studio/Dockerfile.python` - Flask
- `.env.test` - Test environment variables

## Configuration

### Environment Variables (.env)
```
DB_USER=atlantiplex
DB_PASSWORD=change-me-in-production
DB_NAME=atlantiplex
REDIS_PASSWORD=change-me-in-production
JWT_SECRET=your-secret-key
STRIPE_SECRET_KEY=sk_test_...
CORS_ORIGIN=http://localhost
```

### Ports
- **9001**: Node.js Stage Server
- **5000**: Flask Backend API
- **80**: Nginx HTTP
- **443**: Nginx HTTPS
- **5432**: PostgreSQL (internal)
- **6379**: Redis (internal)

## Health Checks

All services have health checks. View status:
```bash
docker-compose ps
```

Expected output:
```
atlantiplex-postgres   Healthy
atlantiplex-redis      Healthy
atlantiplex-stage      Healthy
atlantiplex-flask      Running
atlantiplex-nginx      Up
```

## Common Issues

### Services not starting
```bash
# Check logs
docker logs atlantiplex-postgres

# Clear volumes and restart
docker-compose down -v
docker-compose up -d
```

### Port already in use
```bash
# Find process using port
lsof -i :9001

# Kill process
kill -9 <PID>
```

### Rebuild after code changes
```bash
# Option 1: Rebuild specific service
docker-compose build stage-server

# Option 2: Rebuild all
docker-compose build --no-cache
```

## Production Deployment

```bash
# 1. Build and scan
docker-compose build
docker scout cves atlantiplex-stage:latest

# 2. Push to registry
docker tag atlantiplex-stage:latest registry.example.com/atlantiplex-stage:v1.0.0
docker push registry.example.com/atlantiplex-stage:v1.0.0

# 3. Deploy with docker-compose
docker-compose -f docker-compose.yml up -d

# 4. Monitor
docker-compose ps
docker scout cves atlantiplex-stage:latest
```

## Documentation

- **Optimization Details**: See `DOCKERFILE_OPTIMIZATION_GUIDE.md`
- **Vulnerability Info**: See `VULNERABILITY_REMEDIATION.md`
- **Test Results**: See `E2E_TEST_REPORT.md`
- **Full Summary**: See `E2E_TEST_SUMMARY.md`

---

**Version**: 1.0.0
**Status**: ✅ Production Ready
**Last Updated**: 2026-02-20
