# Atlantiplex Hub - Multi-App Architecture

## Overview

The Atlantiplex Hub is a unified platform consisting of a shared **Gateway Layer** and four specialized applications, all accessible through a single entry point with a consistent header and navigation system.

```
┌────────────────────────────────────────────────────────────┐
│  GATEWAY (Header) ROUTER LOAD BALANCER SHARED COMPONENTS   │
│  Port: 3000                                                 │
└────────────────────────────────────────────────────────────┘
        ↓              ↓               ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  STUDIO APP  │ │  CATALOG APP │ │  ADMIN APP   │ │  DASHBOARD   │
│  Port: 5173  │ │  Port: 5174  │ │  Port: 5175  │ │  Port: 5176  │
│   Creative   │ │ E-Commerce   │ │ Management   │ │   Social     │
│    Suite     │ │    /Shop     │ │  Dashboard   │ │   Engagement │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        ↓              ↓               ↓              ↓
├──────────────────────────────────────────────────────────┤
│            SHARED BACKEND SERVICES                        │
│  PostgreSQL | Redis | API Server | Nginx Proxy          │
└──────────────────────────────────────────────────────────┘
```

## Architecture Components

### 1. Gateway Layer (Port 3000)
**Purpose**: Central routing, unified header/navigation, load balancing

**Responsibilities**:
- Serves shared header component across all apps
- Routes traffic to appropriate sub-applications
- Proxies API calls to backend services
- Provides unified health checks
- Manages shared resources (fonts, icons, etc.)

**Technologies**:
- Express.js for routing
- React/TypeScript for shared UI
- CSS modules for styling

### 2. Atlantiplex Studio (Port 5173)
**Purpose**: Creative content production suite

**Features**:
- Video editing and streaming controls
- Scene composition and effects
- Live broadcast management
- Asset library
- Recording and processing

**Routes**:
- Gateway: `/studio`
- Direct: `http://localhost:5173`

### 3. Product Catalog (Port 5174)
**Purpose**: E-Commerce platform and product management

**Features**:
- Product browsing and search
- Shopping cart management
- Order processing
- Payment integration (Stripe)
- Inventory management

**Routes**:
- Gateway: `/products`
- Direct: `http://localhost:5174`

### 4. Admin Dashboard (Port 5175)
**Purpose**: Administrative and management operations

**Features**:
- User management
- Analytics and reporting
- System configuration
- Content moderation
- Settings management

**Routes**:
- Gateway: `/admin`
- Direct: `http://localhost:5175`

### 5. Dashboard & Social (Port 5176)
**Purpose**: User engagement and social features

**Features**:
- User profiles and dashboards
- Social feeds
- Community interactions
- Notifications
- Personal settings

**Routes**:
- Gateway: `/dashboard`
- Direct: `http://localhost:5176`

## Shared Components

### Directory: `./shared/`

```
shared/
├── components/
│   ├── SharedHeader.tsx      (Navigation bar)
│   ├── ThemeProvider.tsx     (Theme context)
│   └── ...
├── styles/
│   ├── gateway.css           (Header & layout)
│   ├── variables.css         (CSS custom properties)
│   └── ...
├── icons/                     (SVG/icon assets)
├── fonts/                     (Font files)
├── utils/                     (Helper functions)
├── constants/                 (Shared constants)
└── types/                     (TypeScript types)
```

### Shared Styling
- **Primary Color**: `#1a1a2e` (Dark blue)
- **Accent Color**: `#e94560` (Red)
- **Header Height**: 80px fixed
- **Responsive breakpoints**: 1024px, 768px, 480px

## Backend Services

### PostgreSQL
- Shared database for all applications
- Persistent data storage
- Connection pooling

### Redis
- Session management
- Caching layer
- Real-time features

### API Server (Flask)
- RESTful API endpoints
- Business logic
- Authentication/Authorization

## Deployment

### Using Docker Compose

```bash
# Development
docker compose up

# Production
docker compose -f docker-compose.hub.yml up -d

# Build images
DOCKER_BUILDKIT=1 docker compose -f docker-compose.hub.yml build

# Specific service
docker compose -f docker-compose.hub.yml up -d studio catalog admin dashboard
```

### Environment Variables Required

```env
# Database
DB_USER=atlantiplex
DB_PASSWORD=<secure-password>
DB_NAME=atlantiplex

# Redis
REDIS_PASSWORD=<secure-password>

# API Keys
STRIPE_PUBLISHABLE_KEY=<stripe-key>
STRIPE_SECRET_KEY=<stripe-key>

# Services
IMAGE_TAG=latest
```

## Network Communication

### Inter-Service Communication

1. **Gateway to Apps**
   ```
   gateway:3000 → studio:5173
   gateway:3000 → catalog:5174
   gateway:3000 → admin:5175
   gateway:3000 → dashboard:5176
   ```

2. **Apps to Backend**
   ```
   studio:5173 → api:5000 (via gateway proxy)
   catalog:5174 → api:5000 (via gateway proxy)
   admin:5175 → api:5000 (via gateway proxy)
   dashboard:5176 → api:5000 (via gateway proxy)
   ```

3. **Backend to Databases**
   ```
   api:5000 → postgres:5432
   api:5000 → redis:6379
   ```

### Docker Network
- Network: `atlantiplex-hub`
- Type: Bridge network
- Service discovery via DNS (container names)

## Development

### Setup Individual Apps

```bash
# Install dependencies for each app
cd ./apps/atlantiplex-studio && npm install
cd ./apps/product-catalog && npm install
cd ./apps/admin-dashboard && npm install
cd ./apps/dashboard-social && npm install

# Run development servers
npm run dev  # Each app runs on different port
```

### Running Full Stack

```bash
# Option 1: Docker Compose (Recommended for production-like setup)
docker compose -f docker-compose.hub.yml up

# Option 2: Mixed local + Docker (for development)
# Run gateway and apps locally, services in Docker
docker compose -f docker-compose.hub.yml up postgres redis api
npm run dev  # in each app directory
```

## Building and Deployment

### Build All Images

```bash
export DOCKER_BUILDKIT=1
docker compose -f docker-compose.hub.yml build
```

### Build Specific Service

```bash
docker compose -f docker-compose.hub.yml build studio
```

### Push to Registry

```bash
docker tag atlantiplex-gateway:latest myregistry/atlantiplex-gateway:latest
docker push myregistry/atlantiplex-gateway:latest
```

## Health Checks

Each service includes health checks:

```
GET /health  → Returns service status
Interval: 30 seconds
Timeout: 10 seconds
Retries: 3
Start period: 40 seconds
```

Monitor health:
```bash
docker compose -f docker-compose.hub.yml ps
```

## Security

### Network Security
- Services communicate over internal Docker network
- No exposed ports except gateway (3000) and PostgreSQL (optional)
- Redis requires authentication

### Application Security
- All apps run as non-root users
- Non-root user: `nodejs:1001`
- dumb-init for proper signal handling
- Security headers configured in gateway

### Data Security
- Environment variables for secrets (no hardcoding)
- Database passwords required
- API authentication via JWT tokens
- HTTPS ready (configure in reverse proxy)

## Scaling

### Horizontal Scaling

```bash
# Increase replicas in docker-compose
services:
  studio:
    deploy:
      replicas: 3
```

### Resource Limits

Each service has defined resource limits:
```yaml
resources:
  limits:
    cpus: '0.8'
    memory: 512M
  reservations:
    cpus: '0.4'
    memory: 256M
```

## Monitoring

### Logs

```bash
# View all logs
docker compose -f docker-compose.hub.yml logs

# Follow specific service
docker compose -f docker-compose.hub.yml logs -f studio

# Last 100 lines
docker compose -f docker-compose.hub.yml logs --tail 100 api
```

### Metrics

```bash
# Resource usage
docker stats

# Network stats
docker network inspect atlantiplex-hub
```

## Troubleshooting

### Service not responding
```bash
# Check container status
docker compose -f docker-compose.hub.yml ps

# View logs
docker compose -f docker-compose.hub.yml logs <service>

# Restart service
docker compose -f docker-compose.hub.yml restart <service>
```

### Gateway proxy errors
```bash
# Check target URLs
docker compose -f docker-compose.hub.yml exec gateway env | grep VITE

# Test connectivity
docker compose -f docker-compose.hub.yml exec gateway wget -O- http://studio:5173
```

### Database connection issues
```bash
# Check PostgreSQL
docker compose -f docker-compose.hub.yml logs postgres

# Test connection
docker compose -f docker-compose.hub.yml exec api psql $DATABASE_URL -c "SELECT 1"
```

## File Structure Summary

```
atlantiplex-hub/
├── shared/                          # Shared components and styles
│   ├── components/SharedHeader.tsx
│   └── styles/gateway.css
├── gateway/                         # Central routing server
│   ├── server.js
│   ├── package.json
│   └── Dockerfile
├── apps/                            # Individual applications
│   ├── atlantiplex-studio/
│   ├── product-catalog/
│   ├── admin-dashboard/
│   └── dashboard-social/
├── matrix-studio/                   # Backend services
│   ├── Dockerfile.python
│   └── ...
├── docker-compose.hub.yml           # Multi-app orchestration
└── init-architecture.sh             # Setup script
```

## Next Steps

1. **Implement each app's core functionality**
2. **Create shared component library**
3. **Configure authentication and authorization**
4. **Set up CI/CD pipeline for all services**
5. **Configure production reverse proxy (nginx)**
6. **Set up monitoring and logging**
7. **Deploy to production infrastructure**

---

**Last Updated**: 2026-02-25
**Version**: 1.0.0
