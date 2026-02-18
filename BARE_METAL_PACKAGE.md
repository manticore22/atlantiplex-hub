# ATLANTIPLEX STUDIO - BARE METAL DEPLOYMENT PACKAGE
## Complete Self-Hosted Infrastructure

---

## 🏗️ What's Included

This package provides everything needed to deploy Atlantiplex Studio on bare metal servers, VPS, or dedicated hardware.

---

## 📦 Package Contents

### 1. Docker Compose Configuration
**File:** `docker-compose.yml`

Complete multi-service orchestration:
- ✅ PostgreSQL 15 (Database)
- ✅ Redis 7 (Cache)
- ✅ Node.js Stage Server (Port 9001)
- ✅ Python Flask Backend (Port 5000)
- ✅ Nginx Reverse Proxy (Ports 80/443)
- ✅ Frontend Builder

**Features:**
- Health checks on all services
- Persistent volumes for data
- Network isolation
- Automatic restart policies

---

### 2. Nginx Configuration
**Files:**
- `nginx/nginx.conf` - Main configuration
- `nginx/sites-enabled/atlantiplex.conf` - Site configuration

**Features:**
- SSL/TLS termination
- WebSocket proxy support
- Rate limiting
- Gzip compression
- Security headers
- Static file caching

---

### 3. Deployment Scripts

#### Automated Deployment
**File:** `scripts/deploy.sh`

One-command deployment that:
- Updates system packages
- Installs dependencies (Node.js, Python, Docker)
- Configures firewall (UFW)
- Sets up PostgreSQL and Redis
- Generates SSL certificates (Let's Encrypt)
- Clones repository
- Builds and starts containers
- Configures monitoring

**Usage:**
```bash
chmod +x scripts/deploy.sh
sudo DOMAIN=studio.example.com EMAIL=admin@example.com ./scripts/deploy.sh
```

#### Management Script
**File:** `scripts/atlantiplex.sh`

Complete management toolkit:
```bash
# Service management
./scripts/atlantiplex.sh start
./scripts/atlantiplex.sh stop
./scripts/atlantiplex.sh restart
./scripts/atlantiplex.sh status

# Logs
./scripts/atlantiplex.sh logs
./scripts/atlantiplex.sh logs stage-server

# Maintenance
./scripts/atlantiplex.sh update
./scripts/atlantiplex.sh backup
./scripts/atlantiplex.sh restore /path/to/backup.tar.gz
./scripts/atlantiplex.sh stats

# SSL
./scripts/atlantiplex.sh ssl status
./scripts/atlantiplex.sh ssl renew
```

---

### 4. Docker Configurations

#### Python Backend Dockerfile
**File:** `matrix-studio/Dockerfile.python`

Multi-stage build:
- Builder stage with build dependencies
- Production stage with runtime only
- Security-hardened (non-root user)
- Health checks included

#### Existing Node.js Dockerfile
**File:** `matrix-studio/web/stage/Dockerfile`

Optimized Node.js 20 Alpine image

#### Frontend Dockerfile
**File:** `matrix-studio/web/frontend/Dockerfile`

Vite-based build process

---

### 5. Database Initialization
**File:** `init-scripts/01-init.sh`

PostgreSQL setup:
- UUID extension
- Schema creation
- User permissions

---

### 6. Documentation

#### Main Guide
**File:** `BARE_METAL_DEPLOYMENT.md`

Comprehensive 400+ line guide covering:
- System requirements
- Architecture diagrams
- Quick start (automated)
- Manual deployment steps
- VPS provider comparison
- Security checklist
- Performance tuning
- Troubleshooting
- Backup strategy

#### Quick Deploy
**File:** `QUICK_DEPLOY.md`

15-minute deployment guide for Railway + Vercel

#### Full Deployment Guide
**File:** `DEPLOYMENT_GUIDE.md`

Multi-platform deployment options

---

## 🚀 Deployment Options

### Option 1: Automated (Recommended)

```bash
# On fresh Ubuntu 22.04 server
wget https://raw.githubusercontent.com/yourusername/atlantiplex-hub/main/scripts/deploy.sh
chmod +x deploy.sh
sudo DOMAIN=studio.yourdomain.com EMAIL=admin@yourdomain.com ./deploy.sh
```

**Time:** 10-15 minutes
**Complexity:** Low
**Best for:** Quick deployment, testing, production

---

### Option 2: Manual Step-by-Step

Follow `BARE_METAL_DEPLOYMENT.md` for full control.

**Time:** 30-45 minutes
**Complexity:** Medium
**Best for:** Learning, customization, enterprise

---

### Option 3: Docker Compose Only

```bash
# If you already have Docker and databases
git clone https://github.com/yourusername/atlantiplex-hub.git
cd atlantiplex-hub

# Configure environment
cp .env.example .env
nano .env

# Deploy
docker-compose up -d
```

**Time:** 5 minutes
**Complexity:** Low
**Best for:** Existing infrastructure, Kubernetes prep

---

## 💰 VPS Provider Recommendations

### Budget Tier (Development/MVP)

| Provider | Specs | Price | Best For |
|----------|-------|-------|----------|
| **Hetzner CX11** | 1vCPU, 2GB RAM | €4.51/mo | Best value |
| **DigitalOcean** | 1vCPU, 1GB RAM | $6/mo | Reliability |
| **Vultr** | 1vCPU, 1GB RAM | $5/mo | Global locations |

### Production Tier

| Provider | Specs | Price | Best For |
|----------|-------|-------|----------|
| **Hetzner CPX21** | 2vCPU, 4GB RAM | €8.91/mo | Best value |
| **DigitalOcean** | 2vCPU, 4GB RAM | $24/mo | Support |
| **AWS EC2** | 2vCPU, 4GB RAM | ~$30/mo | Enterprise |
| **OVH** | 2vCPU, 4GB RAM | $10/mo | EU compliance |

---

## 🔒 Security Features

### Included
- ✅ UFW firewall configuration
- ✅ Fail2ban intrusion prevention
- ✅ Automatic security updates
- ✅ Let's Encrypt SSL certificates
- ✅ Nginx rate limiting
- ✅ Security headers (HSTS, CSP, etc.)
- ✅ Non-root Docker containers
- ✅ Database isolation

### Additional Recommendations
- Use SSH keys only (disable password auth)
- Enable 2FA for SSH
- Regular security audits
- Log monitoring (fail2ban, logwatch)
- Backup encryption

---

## 📊 Monitoring & Maintenance

### Automatic
- Health checks every 5 minutes (cron)
- SSL certificate auto-renewal
- Log rotation (daily)
- Backup creation (configurable)

### Manual Commands
```bash
# Check status
scripts/atlantiplex.sh status

# View stats
scripts/atlantiplex.sh stats

# View logs
scripts/atlantiplex.sh logs

# Create backup
scripts/atlantiplex.sh backup
```

---

## 🔄 Update Process

### Automated Update
```bash
cd /opt/atlantiplex
scripts/atlantiplex.sh update
```

### Manual Update
```bash
cd /opt/atlantiplex
git pull
docker-compose down
docker-compose up -d --build
```

---

## 🆘 Troubleshooting

### Common Issues

1. **Services won't start**
   ```bash
   docker-compose logs
   systemctl status nginx postgresql redis
   ```

2. **Database connection errors**
   ```bash
   sudo -u postgres psql -c "\l"
   docker-compose exec postgres pg_isready
   ```

3. **SSL certificate issues**
   ```bash
   certbot certificates
   certbot renew --force-renewal
   ```

4. **High memory usage**
   ```bash
   docker stats
   free -h
   ```

---

## 📈 Scaling Options

### Vertical Scaling
```bash
# Upgrade VPS plan
# Restart services
docker-compose restart
```

### Horizontal Scaling (Advanced)
```yaml
# Add to docker-compose.yml
deploy:
  replicas: 2
  resources:
    limits:
      cpus: '2'
      memory: 4G
```

### Load Balancing
- Use Nginx upstream module
- Or deploy behind AWS ALB/CloudFlare

---

## 🎯 Use Cases

### Perfect For:
- ✅ Production streaming platforms
- ✅ High-traffic applications
- ✅ Compliance requirements (GDPR, HIPAA)
- ✅ Custom infrastructure needs
- ✅ Cost optimization at scale
- ✅ Learning Docker/DevOps

### Not Ideal For:
- ❌ Quick prototypes (use Railway/Vercel)
- ❌ Very low traffic (overkill)
- ❌ No technical team available

---

## 📋 Pre-Deployment Checklist

Before running deploy.sh:

- [ ] Domain purchased and DNS configured
- [ ] Server provisioned (Ubuntu 22.04)
- [ ] SSH access configured
- [ ] Stripe account created
- [ ] Stripe API keys obtained
- [ ] Email address for SSL certificates

After deployment:

- [ ] Test payment flow
- [ ] Configure Stripe webhooks
- [ ] Test admin access
- [ ] Verify SSL certificates
- [ ] Test backup/restore
- [ ] Document custom configurations

---

## 🎓 Learning Path

1. **Beginner**: Use automated deploy.sh
2. **Intermediate**: Follow manual deployment guide
3. **Advanced**: Customize Docker Compose, add monitoring
4. **Expert**: Kubernetes migration, CI/CD pipeline

---

## 🔗 Related Documentation

- `BARE_METAL_DEPLOYMENT.md` - Full manual guide
- `DEPLOYMENT_GUIDE.md` - All deployment options
- `QUICK_DEPLOY.md` - 15-minute managed deploy
- `DEPLOYMENT_READINESS_REPORT.md` - Pre-flight checks
- `ABYSSAL_BRIDGE_SUMMARY.md` - Feature overview

---

## 🆘 Support

### Getting Help
1. Check logs: `scripts/atlantiplex.sh logs`
2. Review documentation
3. Search GitHub issues
4. Open new issue with:
   - Error messages
   - Server specs
   - Deployment method used
   - Steps to reproduce

---

## 🎉 Ready to Deploy?

Choose your path:

1. **Fastest**: `sudo ./scripts/deploy.sh`
2. **Most Control**: Follow `BARE_METAL_DEPLOYMENT.md`
3. **Existing Infra**: `docker-compose up -d`

**Your Abyssal Bridge awaits!** 🌊🤖

---

**Version**: 2.0.77  
**Last Updated**: 2026-02-09  
**Compatibility**: Ubuntu 22.04+, Debian 12+, Docker 24+

---

*Built for steel. Engineered for performance. Ready for the abyss.*

**Atlantiplex Systems | Bare Metal Edition**
