# Atlantiplex Studio - Bare Metal Deployment Guide
## For VPS, Dedicated Servers, and On-Premise Infrastructure

---

## 🎯 Overview

This guide covers deploying Atlantiplex Studio on bare metal servers using Docker Compose. Perfect for:
- **VPS Providers**: DigitalOcean, Linode, Vultr, Hetzner, AWS EC2, Azure VMs
- **Dedicated Servers**: OVH, Hetzner Dedicated, Bare Metal Cloud
- **On-Premise**: Self-hosted infrastructure
- **High Performance**: When you need maximum control and performance

---

## 📋 System Requirements

### Minimum Requirements
- **CPU**: 2 vCPUs
- **RAM**: 4GB
- **Storage**: 40GB SSD
- **OS**: Ubuntu 22.04 LTS (recommended) or Debian 12
- **Network**: Public IP address, ports 80/443 open

### Recommended for Production
- **CPU**: 4+ vCPUs
- **RAM**: 8GB+
- **Storage**: 100GB+ NVMe SSD
- **Bandwidth**: 2TB+/month
- **OS**: Ubuntu 22.04 LTS

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        YOUR SERVER                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Nginx     │  │  Stage      │  │  Flask              │  │
│  │  (Reverse   │──│  Server     │──│  Backend            │  │
│  │   Proxy)    │  │  (Node.js)  │  │  (Python)           │  │
│  │  Port 443   │  │  Port 9001  │  │  Port 5000          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  PostgreSQL │  │   Redis     │  │  Static Frontend    │  │
│  │  Database   │  │   Cache     │  │  (Built React App)  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Let's Encrypt  │
                    │   SSL/TLS        │
                    └──────────────────┘
```

---

## 🚀 Quick Start (Automated)

### One-Command Deployment

```bash
# 1. Get a VPS (Ubuntu 22.04)
# Recommended: DigitalOcean Droplet ($6-24/month), Hetzner Cloud (€4.51/month)

# 2. SSH into your server
ssh root@your-server-ip

# 3. Download and run deployment script
wget https://raw.githubusercontent.com/yourusername/atlantiplex-hub/main/scripts/deploy.sh
chmod +x deploy.sh

# 4. Run deployment
DOMAIN=studio.yourdomain.com EMAIL=admin@yourdomain.com ./deploy.sh

# 5. Done! Your app is live at https://studio.yourdomain.com
```

---

## 🔧 Manual Deployment

### Step 1: Server Setup

```bash
# Update system
apt update && apt upgrade -y

# Install required packages
apt install -y curl wget git nginx certbot python3-certbot-nginx \
    postgresql postgresql-contrib redis-server ufw fail2ban

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Install Docker
curl -fsSL https://get.docker.com | sh
usermod -aG docker $USER
systemctl enable docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Step 2: Configure Firewall

```bash
# Setup UFW
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 9001/tcp
ufw --force enable

# Verify
ufw status
```

### Step 3: Clone Repository

```bash
# Create installation directory
mkdir -p /opt/atlantiplex
cd /opt/atlantiplex

# Clone repository
git clone https://github.com/yourusername/atlantiplex-hub.git .

# Or upload your code via SCP
# scp -r ./atlantiplex-hub root@your-server:/opt/atlantiplex
```

### Step 4: Environment Configuration

```bash
# Create environment file
cp .env.example .env

# Edit with your settings
nano .env
```

**Required variables:**
```bash
# Database (auto-generated by deploy script)
DB_USER=atlantiplex
DB_PASSWORD=your_secure_password
DB_NAME=atlantiplex

# JWT Secret (generate with: openssl rand -base64 64)
JWT_SECRET=your_super_secret_key

# Stripe Keys (get from https://dashboard.stripe.com)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Domain
CORS_ORIGIN=https://studio.yourdomain.com
API_URL=https://studio.yourdomain.com
```

### Step 5: Setup Database

```bash
# Start PostgreSQL
systemctl start postgresql
systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE USER atlantiplex WITH PASSWORD 'your_secure_password';
CREATE DATABASE atlantiplex OWNER atlantiplex;
GRANT ALL PRIVILEGES ON DATABASE atlantiplex TO atlantiplex;
\q
EOF

# Start Redis
systemctl start redis-server
systemctl enable redis-server
```

### Step 6: SSL Certificate

```bash
# Generate SSL certificate with Let's Encrypt
certbot certonly --standalone -d studio.yourdomain.com --agree-tos -n -m admin@yourdomain.com

# Copy certificates
mkdir -p /opt/atlantiplex/nginx/ssl
cp /etc/letsencrypt/live/studio.yourdomain.com/fullchain.pem /opt/atlantiplex/nginx/ssl/
cp /etc/letsencrypt/live/studio.yourdomain.com/privkey.pem /opt/atlantiplex/nginx/ssl/

# Setup auto-renewal
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet") | crontab -
```

### Step 7: Configure Nginx

```bash
# Update nginx config with your domain
sed -i 's/YOUR_DOMAIN/studio.yourdomain.com/g' /opt/atlantiplex/nginx/sites-enabled/atlantiplex.conf

# Copy nginx config
cp /opt/atlantiplex/nginx/nginx.conf /etc/nginx/nginx.conf
cp /opt/atlantiplex/nginx/sites-enabled/atlantiplex.conf /etc/nginx/sites-available/atlantiplex
ln -sf /etc/nginx/sites-available/atlantiplex /etc/nginx/sites-enabled/

# Test and reload nginx
nginx -t
systemctl reload nginx
```

### Step 8: Build and Deploy

```bash
cd /opt/atlantiplex

# Build and start containers
docker-compose up -d --build

# Wait for services
sleep 30

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

---

## 💰 VPS Provider Comparison

### Budget Options (Perfect for MVP)

| Provider | Specs | Price | Location |
|----------|-------|-------|----------|
| **Hetzner CX11** | 1 vCPU, 2GB RAM | €4.51/mo | EU |
| **DigitalOcean** | 1 vCPU, 1GB RAM | $6/mo | US/EU/ASIA |
| **Vultr** | 1 vCPU, 1GB RAM | $5/mo | Global |
| **Linode** | 1 vCPU, 1GB RAM | $5/mo | US/EU/ASIA |

### Recommended for Production

| Provider | Specs | Price | Best For |
|----------|-------|-------|----------|
| **Hetzner CPX21** | 2 vCPU, 4GB RAM | €8.91/mo | Best value |
| **DigitalOcean** | 2 vCPU, 4GB RAM | $24/mo | Reliability |
| **AWS EC2 t3.medium** | 2 vCPU, 4GB RAM | ~$30/mo | Enterprise |
| **OVH VPS** | 2 vCPU, 4GB RAM | $10/mo | EU compliance |

---

## 🔒 Security Checklist

### System Security
- [ ] Firewall enabled (UFW)
- [ ] Fail2ban installed
- [ ] SSH key authentication only
- [ ] Root login disabled
- [ ] Automatic security updates
- [ ] Unattended upgrades configured

### Application Security
- [ ] Strong JWT_SECRET (64+ chars)
- [ ] Database passwords secure
- [ ] Stripe webhook signature verified
- [ ] HTTPS only (HSTS enabled)
- [ ] Security headers configured
- [ ] Rate limiting enabled

### Monitoring
- [ ] Log rotation configured
- [ ] Health checks running
- [ ] SSL auto-renewal enabled
- [ ] Backup automation setup
- [ ] Resource monitoring (optional: Grafana)

---

## 📊 Management Commands

After deployment, use the management script:

```bash
# View status
/opt/atlantiplex/scripts/atlantiplex.sh status

# View logs
/opt/atlantiplex/scripts/atlantiplex.sh logs
/opt/atlantiplex/scripts/atlantiplex.sh logs stage-server

# Restart services
/opt/atlantiplex/scripts/atlantiplex.sh restart

# Update to latest version
/opt/atlantiplex/scripts/atlantiplex.sh update

# Backup data
/opt/atlantiplex/scripts/atlantiplex.sh backup

# System stats
/opt/atlantiplex/scripts/atlantiplex.sh stats

# SSL management
/opt/atlantiplex/scripts/atlantiplex.sh ssl status
/opt/atlantiplex/scripts/atlantiplex.sh ssl renew
```

Or use Docker Compose directly:

```bash
cd /opt/atlantiplex

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart stage-server

# Scale services
docker-compose up -d --scale stage-server=2

# Shell access
docker-compose exec stage-server bash
docker-compose exec postgres psql -U atlantiplex
```

---

## 🔧 Troubleshooting

### Issue: Services won't start
```bash
# Check logs
docker-compose logs

# Check specific service
docker-compose logs stage-server

# Verify ports
netstat -tulpn | grep 9001

# Check disk space
df -h
```

### Issue: Database connection failed
```bash
# Check PostgreSQL
systemctl status postgresql

# Verify credentials
sudo -u postgres psql -c "\du"

# Check database exists
sudo -u postgres psql -c "\l"
```

### Issue: SSL certificate errors
```bash
# Test certificate
certbot certificates

# Renew manually
certbot renew --force-renewal

# Check nginx config
nginx -t
```

### Issue: High memory usage
```bash
# View memory usage
docker stats

# Restart services
docker-compose restart

# Add swap (if needed)
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

---

## 📈 Performance Tuning

### For High Traffic (>1000 concurrent users)

1. **Scale PostgreSQL**
```bash
# Edit postgresql.conf
shared_buffers = 2GB
effective_cache_size = 6GB
max_connections = 200
```

2. **Nginx Optimization**
```nginx
worker_processes auto;
worker_connections 4096;
keepalive_timeout 30;
```

3. **Docker Resources**
```yaml
# In docker-compose.yml
services:
  stage-server:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

4. **Enable CDN** (CloudFlare free tier)
   - Sign up at https://cloudflare.com
   - Add your domain
   - Enable caching and DDoS protection

---

## 💾 Backup Strategy

### Automated Backups

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/atlantiplex/scripts/atlantiplex.sh backup

# Sync to S3 (optional)
0 3 * * * aws s3 sync /opt/backups/atlantiplex s3://your-backup-bucket
```

### Manual Backup

```bash
# Create backup
/opt/atlantiplex/scripts/atlantiplex.sh backup

# View backups
ls -la /opt/backups/atlantiplex/

# Restore from backup
/opt/atlantiplex/scripts/atlantiplex.sh restore /opt/backups/atlantiplex/backup_20240115_120000.tar.gz
```

---

## 🆘 Support

### Getting Help

1. **Check Logs**: `docker-compose logs -f`
2. **Health Check**: `scripts/atlantiplex.sh status`
3. **Documentation**: See README files in repository
4. **Community**: Open an issue on GitHub

### Useful Commands

```bash
# Check all service status
systemctl status nginx postgresql redis-server docker

# View resource usage
htop
docker stats

# Network diagnostics
curl -I https://studio.yourdomain.com
netstat -tulpn

# Database queries
sudo -u postgres psql -d atlantiplex -c "SELECT * FROM users LIMIT 5;"
```

---

## ✅ Deployment Checklist

Before going live:

- [ ] Domain configured and pointing to server
- [ ] SSL certificate installed
- [ ] Environment variables set (Stripe keys, JWT secret)
- [ ] Database initialized
- [ ] Firewall configured
- [ ] Services running and healthy
- [ ] Payment flow tested
- [ ] Backup system configured
- [ ] Monitoring enabled
- [ ] SSL auto-renewal verified
- [ ] Documentation updated

---

## 🎉 Success!

Your Atlantiplex Studio is now running on bare metal! Access it at:
- **Web App**: https://studio.yourdomain.com
- **Admin Panel**: https://studio.yourdomain.com/?command=true

**Next Steps:**
1. Configure Stripe webhooks in dashboard
2. Test payment flow
3. Invite team members
4. Monitor performance
5. Scale as needed

---

*Built for performance. Engineered for scale. Ready for the abyss.*

**Atlantiplex Systems | Bare Metal Edition v2.0.77**
