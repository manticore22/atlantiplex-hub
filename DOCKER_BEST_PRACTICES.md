# Docker Containerization Best Practices - Atlantiplex Studio

## ✅ Docker Best Practices Implemented

### 1. Multi-Stage Builds
All Dockerfiles use multi-stage builds to minimize final image size:
- **Node.js Stage Server**: Dependencies stage → Runtime stage (removes build tools from final image)
- **React Frontend**: Builder stage → Nginx runtime stage (only dist files copied)
- **Python Flask**: Builder stage with venv → Runtime stage (removes build dependencies)

**Benefits:**
- Reduces final image size by 50-70%
- Faster runtime performance
- Smaller security surface area

### 2. Non-Root User Execution
All containers run as non-root users for security:
- Node.js: Uses built-in `node` user
- Python: Uses dedicated `app` user
- Nginx: Uses `nginx` user

**Benefits:**
- Prevents privilege escalation attacks
- Follows Docker security best practices
- Limits container breakout impact

### 3. Layer Caching Optimization
Dockerfiles ordered for maximum cache efficiency:
- Copy `package*.json` before source code (Node.js)
- Copy `requirements.txt` before application code (Python)
- Dependencies installed before application copy

**Benefits:**
- Faster rebuilds when source code changes
- Minimal layer re-creation
- Efficient CI/CD pipeline execution

### 4. Health Checks
All services include health checks:
```yaml
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3
```

**Benefits:**
- Docker Compose/Swarm can detect and restart unhealthy containers
- Orchestrators can perform intelligent scheduling
- Better observability of application state

### 5. Signal Handling with dumb-init
All Node.js and Python containers use `dumb-init`:
- Properly forwards Unix signals (SIGTERM, SIGKILL)
- Prevents zombie processes
- Graceful shutdown on container stop

**Benefits:**
- Clean shutdown sequence
- No dangling processes
- Proper log flushing before exit

### 6. Security Configurations

#### Dockerfile Security:
- `USER` clause ensures non-root execution
- `.dockerignore` prevents sensitive files from being copied
- Minimal base images (Alpine Linux)
- No secrets in Dockerfile or image

#### docker-compose.yml Security:
```yaml
security_opt:
  - no-new-privileges:true
cap_drop:
  - ALL
cap_add:
  - NET_BIND_SERVICE  # Only required capabilities
read_only_root_filesystem: true  # Nginx: immutable runtime
tmpfs: [/var/run, /var/cache/nginx]  # Temporary writable mounts
```

**Benefits:**
- Principle of least privilege
- Reduced attack surface
- Container escape prevention

### 7. Volume Management
Volumes configured for persistent data:
- PostgreSQL data: `postgres_data`
- Redis data: `redis_data`
- Application logs: `stage_logs`, `flask_logs`, `nginx_logs`
- File uploads: `stage_uploads`, `flask_recordings`
- Frontend build: `frontend_build`

**Benefits:**
- Data persistence across container restarts
- Easy backup and migration
- Separation of concerns

### 8. Environment Configuration
All services use `.env` file for configuration:
- Database credentials
- JWT secrets
- Stripe API keys
- Redis password
- CORS origins
- Log levels

**Best Practice:**
Create `.env` file from `.env.example`:
```bash
cp .env.example .env
# Edit .env with production values
```

### 9. Networking
Custom bridge network `atlantiplex-network`:
- Services communicate by name (service discovery)
- Isolated from host network
- Subnet configured for predictable IPs

**Benefits:**
- Service-to-service communication
- Network isolation
- Predictable networking

### 10. Resource Limits
Configure in production docker-compose:
```yaml
resources:
  limits:
    cpus: '1'
    memory: 1G
  reservations:
    cpus: '0.5'
    memory: 512M
```

### 11. .dockerignore Optimization
Comprehensive `.dockerignore` includes:
- Version control files
- Development dependencies
- IDE/editor configurations
- Build artifacts
- Documentation
- CI/CD files
- Environment files

**Benefits:**
- Smaller build context
- Faster builds
- No secrets in images

### 12. Image Tagging Strategy
Images tagged with version and `latest`:
```yaml
image: atlantiplex-stage:latest
image: atlantiplex-flask:latest
image: atlantiplex-frontend:latest
```

## 📋 Running the Application

### Development Setup
```bash
# 1. Create environment file
cp .env.example .env

# 2. Build all images
docker compose build

# 3. Build frontend and start all services
docker compose --profile build up -d

# 4. Check status
docker compose ps
docker compose logs -f
```

### Production Deployment
```bash
# 1. Set production environment variables
export DB_PASSWORD=secure-password-here
export JWT_SECRET=secure-jwt-here
export REDIS_PASSWORD=secure-redis-here

# 2. Build with build cache
docker compose build --no-cache

# 3. Start services
docker compose up -d

# 4. Monitor health
docker compose ps
docker compose logs flask-backend
```

### Useful Commands
```bash
# View logs for specific service
docker compose logs -f stage-server

# Execute command in container
docker compose exec flask-backend bash

# Rebuild specific service
docker compose build flask-backend

# Stop all services
docker compose down

# Remove volumes (careful in production!)
docker compose down -v
```

## 🔒 Security Checklist

- [ ] Change default passwords in `.env`
- [ ] Use strong JWT secrets
- [ ] Enable SSL/TLS in Nginx for production
- [ ] Restrict Redis to internal network only
- [ ] Use secrets management (Docker Secrets for Swarm)
- [ ] Enable audit logging
- [ ] Regular image vulnerability scans with Docker Scout
- [ ] Keep base images updated (postgres:15-alpine, node:20-alpine, etc.)

## 📊 Performance Optimizations

1. **Build Cache**: Reuse layers across builds with `cache_from`
2. **Alpine Base Images**: ~50MB vs 300MB+ for full distributions
3. **Production Dependencies Only**: No development tools in final images
4. **Memory Limits**: Node: 512MB, Flask: Limited by system
5. **Connection Pooling**: Configure in application code

## 🚀 Scaling Considerations

1. **Docker Swarm**: For multi-node deployments
   ```bash
   docker swarm init
   docker stack deploy -c docker-compose.yml atlantiplex
   ```

2. **Kubernetes**: For enterprise scaling
   - Use `docker compose convert` to generate manifests
   - Add PersistentVolumes for PostgreSQL/Redis
   - Configure resource requests/limits

3. **Load Balancing**: Update Nginx upstream to point to multiple instances

## ✨ Key Improvements Over Previous Version

1. Added `dumb-init` for proper signal handling
2. Improved layer caching in Node.js Dockerfile
3. Enhanced security with `cap_drop` and `cap_add`
4. Read-only root filesystem for Nginx
5. Comprehensive .dockerignore file
6. Better volume organization with subdirectories
7. Production-ready environment variable handling
8. Health checks with proper start periods
9. Fixed syntax errors in frontend code
10. Removed optional npm packages for reliability

## 📚 Further Reading

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Compose File Reference](https://docs.docker.com/compose/compose-file/)
- [Alpine Linux](https://alpinelinux.org/)
