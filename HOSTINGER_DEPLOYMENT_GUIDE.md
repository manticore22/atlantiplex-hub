# Hostinger Deployment Guide - Atlantiplex Studio

**Status**: Ready for Production
**Last Updated**: 2026-02-20
**Version**: 1.0.0

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Hostinger Account Setup](#hostinger-account-setup)
3. [VPS Configuration](#vps-configuration)
4. [Application Deployment](#application-deployment)
5. [Domain & SSL Setup](#domain--ssl-setup)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- [ ] Hostinger account created
- [ ] VPS plan selected (recommended: 8GB RAM minimum)
- [ ] SSH key pair generated locally
- [ ] Docker Desktop installed locally
- [ ] All service credentials ready (Stripe, email, etc.)
- [ ] Domain name registered
- [ ] Team access to production credentials vault

### Local Requirements

```bash
# Check requirements
docker --version
docker-compose --version
git --version
ssh -V

# Expected versions
# Docker: 20.10+
# Docker Compose: v2.0+
# Git: 2.30+
# OpenSSH: 7.4+
```

---

## Hostinger Account Setup

### 1. Create Hostinger Account

1. Visit [hostinger.com](https://www.hostinger.com)
2. Click "Get Hosting"
3. Select VPS plan:
   - **Recommended**: Business VPS (8GB RAM, 160GB SSD, 4 vCPU)
   - **Minimum**: Standard VPS (4GB RAM, 60GB SSD, 2 vCPU)
4. Complete payment

### 2. Access Your VPS

```bash
# Get SSH credentials from Hostinger dashboard:
# - IP Address
# - Username (usually "root" or custom user)
# - Port (usually 22)

# Test connection
ssh -p 22 root@YOUR_VPS_IP
# Or with key
ssh -i ~/.ssh/hostinger_key -p 22 root@YOUR_VPS_IP
```

### 3. SSH Key Setup (Recommended)

Generate local SSH key:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/hostinger_key -C "atlantiplex@production"
```

Add public key to Hostinger:

```bash
# Copy public key
cat ~/.ssh/hostinger_key.pub | pbcopy  # macOS
# Or manually copy content

# Then paste into Hostinger dashboard under SSH Keys
```

Update local SSH config (`~/.ssh/config`):

```
Host hostinger-prod
    HostName YOUR_VPS_IP
    User root
    Port 22
    IdentityFile ~/.ssh/hostinger_key
    StrictHostKeyChecking accept-new
```

Test connection:

```bash
ssh hostinger-prod
```

---

## VPS Configuration

### 1. Run Initial Setup Script

```bash
# Download and run setup script
ssh hostinger-prod 'bash -s' < setup-hostinger.sh
```

This script will:
- Update system packages
- Install Docker and Docker Compose
- Set up firewall rules
- Configure SSL certificates
- Set up monitoring and backups

### 2. Manual Configuration (If Script Fails)

#### System Updates

```bash
ssh hostinger-prod << 'EOF'
apt-get update
apt-get upgrade -y
apt-get install -y curl wget git vim htop net-tools ufw fail2ban
EOF
```

#### Install Docker

```bash
ssh hostinger-prod << 'EOF'
curl -fsSL https://get.docker.com -o get-docker.sh
bash get-docker.sh
docker --version
EOF
```

#### Install Docker Compose

```bash
ssh hostinger-prod << 'EOF'
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
docker-compose --version
EOF
```

### 3. Create Application User

```bash
ssh hostinger-prod << 'EOF'
useradd -m -s /bin/bash atlantiplex
usermod -aG docker atlantiplex
mkdir -p /home/atlantiplex/{data,logs,backups}
chown -R atlantiplex:atlantiplex /home/atlantiplex
EOF
```

### 4. Configure Firewall

```bash
ssh hostinger-prod << 'EOF'
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw default deny incoming
ufw default allow outgoing
EOF
```

---

## Application Deployment

### 1. Prepare Local Environment

```bash
# Clone or navigate to project directory
cd /path/to/atlantiplex-studio

# Build Docker images locally first
docker-compose build

# Scan for vulnerabilities
docker scout cves atlantiplex-stage:latest
docker scout cves atlantiplex-flask:latest
```

### 2. Create Production Environment File

```bash
# Copy template
cp .env.production.template .env.production

# Edit with production values
nano .env.production

# Required changes:
# - DB_PASSWORD (strong, unique)
# - REDIS_PASSWORD (strong, unique)
# - JWT_SECRET (32+ character random)
# - STRIPE keys
# - Email configuration
# - Domain name references
```

### 3. Push Images to Registry

```bash
# Login to Docker Hub
docker login

# Tag images
docker tag atlantiplex-stage:latest yourusername/atlantiplex-stage:latest
docker tag atlantiplex-flask:latest yourusername/atlantiplex-flask:latest
docker tag atlantiplex-frontend:latest yourusername/atlantiplex-frontend:latest

# Push images
docker push yourusername/atlantiplex-stage:latest
docker push yourusername/atlantiplex-flask:latest
docker push yourusername/atlantiplex-frontend:latest
```

### 4. Deploy to Hostinger

```bash
# Make deploy script executable
chmod +x deploy-hostinger.sh

# Run deployment
./deploy-hostinger.sh production latest

# The script will:
# - Verify prerequisites
# - Backup current database
# - Copy files to server
# - Pull Docker images
# - Start containers
# - Run health checks
```

### 5. Verify Deployment

```bash
# SSH into server
ssh hostinger-prod

# Check service status
cd /home/atlantiplex
docker-compose ps

# View logs
docker-compose logs -f

# Test health endpoints
curl http://localhost:9001/health
curl http://localhost:5000/api/health
```

---

## Domain & SSL Setup

### 1. Point Domain to Hostinger

In your domain registrar's DNS settings, create:

```
A Record: your-domain.com      → YOUR_VPS_IP
A Record: www.your-domain.com  → YOUR_VPS_IP
MX Record: mail.your-domain.com → YOUR_MAIL_SERVER (if email)
TXT Record: v=spf1 include:...  → (SPF record from email provider)
```

**Wait 24-48 hours for DNS propagation.**

### 2. Verify DNS Propagation

```bash
# Check DNS resolution
nslookup your-domain.com
dig your-domain.com
ping your-domain.com

# Expected: Should resolve to YOUR_VPS_IP
```

### 3. Get SSL Certificate (Let's Encrypt)

The setup script should have already handled this. To manually renew:

```bash
ssh hostinger-prod << 'EOF'
certbot renew --quiet
systemctl restart nginx
EOF
```

### 4. Configure Nginx

```bash
# SSH into server
ssh hostinger-prod

# Edit Nginx config
nano /etc/nginx/sites-available/default

# Replace YOUR_DOMAIN with your actual domain
# Example config provided in setup-hostinger.sh
```

Reload Nginx:

```bash
ssh hostinger-prod << 'EOF'
nginx -t  # Test config
systemctl reload nginx
EOF
```

### 5. Test HTTPS

```bash
# Visit your domain
https://your-domain.com

# Should show your application (no SSL warnings)
```

---

## Monitoring & Maintenance

### 1. View Logs

```bash
# SSH into server
ssh hostinger-prod

# View all logs
docker-compose logs -f

# View specific service
docker logs -f atlantiplex-flask
docker logs -f atlantiplex-stage
docker logs -f atlantiplex-postgres
```

### 2. Monitor Performance

```bash
# SSH into server
ssh hostinger-prod

# Check system resources
htop

# Check Docker resource usage
docker stats

# Check disk space
df -h
```

### 3. Database Backup

Backups are automated (daily at 2 AM). Manual backup:

```bash
ssh hostinger-prod << 'EOF'
cd /home/atlantiplex
docker exec atlantiplex-postgres pg_dump -U atlantiplex atlantiplex > backups/manual_backup_$(date +%Y%m%d).sql
gzip backups/manual_backup_*.sql
EOF
```

### 4. Restart Services

If services become unresponsive:

```bash
ssh hostinger-prod << 'EOF'
cd /home/atlantiplex
docker-compose restart
# Or specific service
docker-compose restart atlantiplex-flask
EOF
```

### 5. Update Application

When you have new code:

```bash
# Rebuild and push images
docker-compose build
docker push yourusername/atlantiplex-stage:latest
docker push yourusername/atlantiplex-flask:latest

# Deploy (automatic backup happens)
./deploy-hostinger.sh production latest
```

---

## Troubleshooting

### Services Not Starting

**Problem**: `docker-compose up` fails

**Solution**:

```bash
ssh hostinger-prod << 'EOF'
cd /home/atlantiplex

# Check logs
docker-compose logs

# Common issues:
# 1. Port already in use
netstat -tulpn | grep LISTEN

# 2. Out of disk space
df -h

# 3. Out of memory
free -h

# 4. Docker daemon not running
systemctl status docker
systemctl restart docker
EOF
```

### Database Connection Error

**Problem**: Applications can't connect to database

**Solution**:

```bash
ssh hostinger-prod << 'EOF'
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection
docker exec atlantiplex-postgres pg_isready -U atlantiplex -d atlantiplex

# Check environment variables
docker exec atlantiplex-flask env | grep DB_
EOF
```

### High Memory Usage

**Problem**: Server running slowly, memory usage high

**Solution**:

```bash
ssh hostinger-prod << 'EOF'
# Check memory usage
docker stats

# Identify culprit
docker top CONTAINER_NAME

# Restart container
docker restart CONTAINER_NAME

# If persistent, scale down or upgrade VPS
EOF
```

### SSL Certificate Expired

**Problem**: HTTPS warnings or certificate errors

**Solution**:

```bash
ssh hostinger-prod << 'EOF'
# Check certificate expiry
openssl x509 -in /etc/letsencrypt/live/your-domain/cert.pem -noout -dates

# Renew certificate
certbot renew --force-renewal

# Restart Nginx
systemctl restart nginx
EOF
```

### Application Crashes

**Problem**: Application repeatedly crashes

**Solution**:

```bash
# Check logs
docker-compose logs --tail 100 atlantiplex-flask

# Common causes:
# 1. Database connection lost → restart PostgreSQL
# 2. Out of memory → increase Docker memory limit
# 3. Syntax error → check recent code changes
# 4. Missing environment variable → verify .env file

# Restart service
docker-compose restart atlantiplex-flask
```

### DNS Not Resolving

**Problem**: Domain not resolving to server

**Solution**:

```bash
# Check DNS records
nslookup your-domain.com
dig your-domain.com @8.8.8.8

# Wait 24-48 hours for propagation
# Check with: https://mxtoolbox.com/

# If stuck, check with registrar that DNS servers are set correctly
```

---

## Scaling & Performance

### Increase Resources

If traffic increases, upgrade Hostinger VPS:

1. Go to Hostinger dashboard
2. Select your VPS
3. Click "Upgrade"
4. Select higher tier (more RAM, CPU, disk)
5. Accept billing changes
6. System restarts automatically

### Implement Caching

```bash
# Redis is already configured
# For aggressive caching, set:
CACHE_TTL=86400  # 24 hours
REDIS_MAXMEMORY=1g
```

### Enable CDN

For static assets, enable Cloudflare:

1. Create Cloudflare account
2. Add domain
3. Update DNS servers
4. Configure caching rules

---

## Disaster Recovery

### Restore from Backup

```bash
ssh hostinger-prod << 'EOF'
# List backups
ls -la /home/atlantiplex/backups/

# Restore database
gunzip -c /home/atlantiplex/backups/postgres_YYYYMMDD.sql.gz | \
  docker exec -i atlantiplex-postgres psql -U atlantiplex -d atlantiplex

# Restore application data
tar -xzf /home/atlantiplex/backups/data_YYYYMMDD.tar.gz -C /home/atlantiplex
EOF
```

### Full System Restore

If VPS is lost:

1. Provision new VPS
2. Run `setup-hostinger.sh` again
3. Run `deploy-hostinger.sh production latest`
4. Restore database from backup
5. Point domain to new IP

---

## Support & Resources

- **Hostinger Support**: https://www.hostinger.com/help
- **Docker Docs**: https://docs.docker.com
- **PostgreSQL Docs**: https://www.postgresql.org/docs
- **Nginx Docs**: https://nginx.org/docs
- **Let's Encrypt**: https://letsencrypt.org/docs

---

## Rollback Procedure

If deployment goes wrong:

```bash
./deploy-hostinger.sh rollback

# Or manually:
ssh hostinger-prod << 'EOF'
cd /home/atlantiplex
docker-compose down
git checkout HEAD~1
docker-compose up -d
EOF
```

---

## Sign-Off

- [ ] Production environment verified
- [ ] All credentials secured
- [ ] SSL certificate working
- [ ] Database backed up
- [ ] Monitoring configured
- [ ] Team trained on procedures
- [ ] Ready for launch

---

**Deployment completed successfully!**

For questions or issues, contact the DevOps team.
