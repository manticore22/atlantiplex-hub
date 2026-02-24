# Atlantiplex Hub - Quick Start Guide

## 🚀 Quick Launch (Docker Compose)

### 1. Set Environment Variables

```bash
# Create .env file in project root
cat > .env << EOF
# Database
DB_USER=atlantiplex
DB_PASSWORD=your-secure-password
DB_NAME=atlantiplex

# Redis
REDIS_PASSWORD=your-redis-password

# Stripe (optional)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

# Image
IMAGE_TAG=latest
EOF
```

### 2. Launch Full Stack

```bash
# Build and start all services
export DOCKER_BUILDKIT=1
docker compose -f docker-compose.hub.yml up -d

# Check status
docker compose -f docker-compose.hub.yml ps
```

### 3. Access the Platform

- **Gateway (Main Entry)**: http://localhost:3000
  - Studio: http://localhost:3000/studio
  - Catalog: http://localhost:3000/products
  - Admin: http://localhost:3000/admin
  - Dashboard: http://localhost:3000/dashboard

- **Direct App Access** (for debugging):
  - Studio: http://localhost:5173
  - Catalog: http://localhost:5174
  - Admin: http://localhost:5175
  - Dashboard: http://localhost:5176

### 4. Verify Health

```bash
# Check gateway health
curl http://localhost:3000/health

# Check individual app health
curl http://localhost:5173
curl http://localhost:5174
curl http://localhost:5175
curl http://localhost:5176

# Check backend API
curl http://localhost:5000/api/health
```

---

## 🛠️ Development Setup

### Prerequisites
- Node.js 18+
- Docker & Docker Compose
- Git

### Option 1: Full Docker Setup (Recommended)

```bash
# Clone and setup
git clone <repo-url>
cd atlantiplex-hub

# Copy environment template
cp .env.example .env
# Edit .env with your values

# Build all images
export DOCKER_BUILDKIT=1
docker compose -f docker-compose.hub.yml build

# Start services
docker compose -f docker-compose.hub.yml up -d

# View logs
docker compose -f docker-compose.hub.yml logs -f
```

### Option 2: Mixed Local + Docker

Useful for active development on one app while others run in Docker.

```bash
# Start backend services only (PostgreSQL, Redis, API)
docker compose -f docker-compose.hub.yml up -d postgres redis api

# In each app directory, install and run locally:
cd ./apps/atlantiplex-studio
npm install
npm run dev

# In another terminal:
cd ./apps/product-catalog
npm install
npm run dev

# Run gateway (in another terminal):
cd ./gateway
npm install
npm run dev
```

---

## 📦 Building for Production

### Build All Services

```bash
export DOCKER_BUILDKIT=1

# Build all
docker compose -f docker-compose.hub.yml build

# Build specific service
docker compose -f docker-compose.hub.yml build studio
```

### Push to Registry

```bash
# Login to Docker Registry
docker login

# Tag images
docker tag atlantiplex-gateway:latest your-registry/atlantiplex-gateway:latest
docker tag atlantiplex-studio:latest your-registry/atlantiplex-studio:latest
# ... repeat for all services

# Push
docker push your-registry/atlantiplex-gateway:latest
docker push your-registry/atlantiplex-studio:latest
# ... repeat for all services
```

---

## 🔍 Common Commands

### Container Management

```bash
# View all containers
docker compose -f docker-compose.hub.yml ps

# View logs
docker compose -f docker-compose.hub.yml logs -f <service>

# Restart service
docker compose -f docker-compose.hub.yml restart <service>

# Stop all
docker compose -f docker-compose.hub.yml down

# Stop with volume cleanup
docker compose -f docker-compose.hub.yml down -v
```

### Database Operations

```bash
# Access PostgreSQL
docker compose -f docker-compose.hub.yml exec postgres psql -U atlantiplex -d atlantiplex

# Access Redis
docker compose -f docker-compose.hub.yml exec redis redis-cli -a $REDIS_PASSWORD

# View database size
docker compose -f docker-compose.hub.yml exec postgres psql -U atlantiplex -d atlantiplex -c "SELECT pg_size_pretty(pg_database_size('atlantiplex'));"
```

### API Testing

```bash
# Health check all services
for service in gateway studio catalog admin dashboard api; do
  echo "=== $service ==="
  curl -s http://localhost:3000/health || echo "Gateway error"
done

# Check specific endpoints
curl http://localhost:3000/api/health
curl http://localhost:5000/api/health
```

---

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs for errors
docker compose -f docker-compose.hub.yml logs <service>

# Restart the service
docker compose -f docker-compose.hub.yml restart <service>

# Rebuild and restart
docker compose -f docker-compose.hub.yml build --no-cache <service>
docker compose -f docker-compose.hub.yml up -d <service>
```

### Port Already in Use

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
docker compose -f docker-compose.hub.yml up -d \
  -e "GATEWAY_PORT=3001"
```

### Database Connection Failed

```bash
# Verify PostgreSQL is running
docker compose -f docker-compose.hub.yml ps postgres

# Check logs
docker compose -f docker-compose.hub.yml logs postgres

# Verify environment variables
docker compose -f docker-compose.hub.yml exec postgres env | grep POSTGRES

# Wait for database to be ready
docker compose -f docker-compose.hub.yml exec api \
  until PGPASSWORD=$DB_PASSWORD psql -h postgres -U $DB_USER -d $DB_NAME -c "SELECT 1"; do sleep 1; done
```

### Gateway Can't Connect to Apps

```bash
# Verify app services are running
docker compose -f docker-compose.hub.yml ps studio catalog admin dashboard

# Test connectivity from gateway to app
docker compose -f docker-compose.hub.yml exec gateway \
  wget -O- http://studio:5173

# Check gateway logs for proxy errors
docker compose -f docker-compose.hub.yml logs gateway | grep -i error
```

---

## 📊 Monitoring

### Docker Stats

```bash
# Real-time resource usage
docker stats --no-stream

# Specific service
docker compose -f docker-compose.hub.yml stats
```

### Logs Analysis

```bash
# Last 50 lines
docker compose -f docker-compose.hub.yml logs --tail 50

# Follow logs with timestamps
docker compose -f docker-compose.hub.yml logs -t -f

# Specific time range
docker compose -f docker-compose.hub.yml logs --since 5m --until 1m
```

### Service Health

```bash
# Check all health statuses
docker compose -f docker-compose.hub.yml ps

# Details for a service
docker inspect <container-id>

# Network connectivity
docker network inspect atlantiplex-hub
```

---

## 🔐 Security

### Default Ports
- Gateway: `3000`
- Studio: `5173` (internal)
- Catalog: `5174` (internal)
- Admin: `5175` (internal)
- Dashboard: `5176` (internal)
- API: `5000` (internal)
- PostgreSQL: `5432` (internal, optional expose)
- Redis: `6379` (internal, auth required)

### Recommended Security Measures

1. **Change default passwords** in `.env`
2. **Use strong secrets** for JWT_SECRET, REDIS_PASSWORD
3. **Enable HTTPS** with reverse proxy (nginx)
4. **Restrict database access** to internal network only
5. **Use network policies** in Kubernetes
6. **Enable audit logging** for admin operations
7. **Regular backups** of PostgreSQL

---

## 📚 Project Structure

```
atlantiplex-hub/
├── .env                              # Environment variables
├── .env.example                      # Template
├── docker-compose.hub.yml            # Multi-app orchestration
├── init-architecture.sh              # Setup script
├── ARCHITECTURE_MULTI_APP.md         # This file
│
├── shared/                           # Shared across all apps
│   ├── components/
│   │   └── SharedHeader.tsx
│   ├── styles/
│   │   ├── gateway.css
│   │   └── variables.css
│   ├── icons/
│   ├── fonts/
│   ├── utils/
│   └── constants/
│
├── gateway/                          # Central router
│   ├── server.js
│   ├── package.json
│   └── Dockerfile
│
└── apps/                             # Individual applications
    ├── atlantiplex-studio/
    │   ├── src/
    │   ├── package.json
    │   └── Dockerfile
    ├── product-catalog/
    ├── admin-dashboard/
    └── dashboard-social/
```

---

## 🚢 Deployment

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.hub.yml atlantiplex

# Check status
docker stack services atlantiplex
```

### Kubernetes

```bash
# Build and push images
docker compose -f docker-compose.hub.yml push

# Create namespace
kubectl create namespace atlantiplex

# Deploy (requires k8s manifests - TBD)
kubectl apply -f k8s/ -n atlantiplex
```

### Manual Server Deployment

1. Transfer images to server
2. Load images: `docker load -i image.tar`
3. Configure `.env`
4. Run: `docker compose -f docker-compose.hub.yml up -d`

---

## 📖 Additional Resources

- **Architecture**: See `ARCHITECTURE_MULTI_APP.md`
- **Docker Optimization**: See `PRODUCTION_DOCKERFILE_OPTIMIZATION.md`
- **API Documentation**: See `API_DOCUMENTATION.md`
- **Deployment Guide**: See `DEPLOYMENT_GUIDE.md`

---

## ⚡ Performance Tips

1. **Enable BuildKit** for faster builds
   ```bash
   export DOCKER_BUILDKIT=1
   ```

2. **Use layer caching** - package.json before source code

3. **Limit resources** - set appropriate limits in compose file

4. **Use volume mounts** - for development code synchronization

5. **Implement CDN** - for static assets in production

6. **Database indexing** - ensure proper indexing for queries

7. **Connection pooling** - configure for database connections

---

**For detailed troubleshooting, check individual service logs:**
```bash
docker compose -f docker-compose.hub.yml logs <service-name>
```

Need help? Run:
```bash
docker compose -f docker-compose.hub.yml ps
docker compose -f docker-compose.hub.yml logs
```
