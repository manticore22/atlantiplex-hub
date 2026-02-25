# Atlantiplex Project - Production Deployment

## Deployment Options

### 1. Hostinger VPS (Recommended for Quick Deployment)

**Best for:** Small to medium workloads, cost-effective, easy management

Directory: `./hostinger-deployment/`

Quick start:
```bash
cd hostinger-deployment
cp .env.example .env
nano .env  # Configure
bash deploy.sh
```

**What's included:**
- Docker Compose with all services
- Nginx reverse proxy with multi-domain routing
- PostgreSQL + Redis
- SSL/TLS support
- Automated backup script

**Cost:** ~$5-15/month on Hostinger VPS

---

### 2. Kubernetes (For Enterprise/Scalability)

**Best for:** Large scale, auto-scaling, enterprise deployments

Directory: `./k8s-optimized/`

Quick start:
```bash
cd k8s-optimized
./deploy.sh
```

**What's included:**
- StatefulSets for databases
- Deployments with HPA (auto-scaling)
- Ingress controller
- Network policies
- Resource quotas

**Cost:** Varies by provider ($10-100+/month depending on scale)

---

### 3. Docker Hub + VPS (Manual Docker)

**Best for:** Full control, custom configurations

Quick start:
```bash
# Build and push images to registry
docker build -f AtlantiplexStudio/Dockerfile -t your-registry/atlantiplex-frontend:latest .
docker push your-registry/atlantiplex-frontend:latest

# Deploy with docker-compose or docker run
docker-compose -f docker-compose.prod.yml up -d
```

---

## Project Structure After Cleanup

```
atlantiplex-hub/
├── hostinger-deployment/          ← Hostinger VPS setup
│   ├── docker-compose.yml
│   ├── .env.example
│   ├── deploy.sh
│   ├── backup.sh
│   ├── nginx/
│   ├── ssl/
│   └── README.md
│
├── k8s-optimized/                 ← Kubernetes manifests
│   ├── 00-namespace-config.yaml
│   ├── 01-postgres.yaml
│   ├── ... (6 more manifests)
│   ├── deploy.sh
│   └── README.md
│
├── AtlantiplexStudio/             ← Studio app
│   ├── Dockerfile
│   ├── package.json
│   ├── src/
│   └── ...
│
├── website/                       ← Marketing website
│   ├── Dockerfile
│   ├── package.json
│   ├── src/
│   └── ...
│
├── matrix-studio/                 ← Flask backend
│   ├── Dockerfile.python
│   ├── requirements.txt
│   ├── app.py
│   └── ...
│
├── docker-compose.yml             ← Development setup
├── docker-compose.prod.yml        ← Production Docker Compose
├── docker-compose.dev.yml         ← Development with hot reload
├── .dockerignore
├── .env.example
├── .gitignore
├── README.md
└── docs/                          ← Documentation
    ├── DEPLOYMENT.md
    ├── DOCKER.md
    └── KUBERNETES.md
```

---

## Step-by-Step: Hostinger Deployment

### Prerequisites
1. Hostinger VPS with Docker + Docker Compose installed
2. Domain name registered
3. SSH access to VPS

### Step 1: SSH into VPS

```bash
ssh user@your-hostinger-ip
cd /home/user/atlantiplex
```

### Step 2: Clone Repository

```bash
git clone https://github.com/manticore22/atlantiplex-hub.git
cd atlantiplex-hub/hostinger-deployment
```

### Step 3: Configure Environment

```bash
cp .env.example .env
nano .env

# Change these values:
# DB_PASSWORD=your-strong-password
# REDIS_PASSWORD=your-redis-password
# JWT_SECRET=your-jwt-secret
# STRIPE_SECRET_KEY=sk_live_...
# STRIPE_PUBLISHABLE_KEY=pk_live_...
# STRIPE_WEBHOOK_SECRET=whsec_...
```

### Step 4: Update Domain Names

```bash
# Edit nginx configs with your domain
sed -i 's/atlantiplex.com/your-domain.com/g' nginx/conf.d/*.conf

# Verify changes
cat nginx/conf.d/website.conf | grep server_name
```

### Step 5: Generate SSL Certificates

```bash
# Stop services first
docker-compose down

# Generate with Let's Encrypt
sudo certbot certonly --standalone \
  -d your-domain.com \
  -d www.your-domain.com \
  -d studio.your-domain.com \
  -d api.your-domain.com

# Copy to nginx
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/atlantiplex.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/atlantiplex.key
sudo chown $USER:$USER nginx/ssl/*
```

### Step 6: Deploy

```bash
bash deploy.sh
```

### Step 7: Verify

```bash
# Check services running
docker-compose ps

# View logs
docker-compose logs -f

# Test in browser
curl https://your-domain.com
curl https://studio.your-domain.com
curl https://api.your-domain.com/api/health
```

---

## DNS Setup

Point your domains to your Hostinger VPS IP:

| Domain | Type | Value |
|--------|------|-------|
| your-domain.com | A | YOUR_HOSTINGER_IP |
| www.your-domain.com | A | YOUR_HOSTINGER_IP |
| studio.your-domain.com | A | YOUR_HOSTINGER_IP |
| api.your-domain.com | A | YOUR_HOSTINGER_IP |

Or use CNAME if Hostinger provides a subdomain:
| your-domain.com | CNAME | hostinger.your-domain.com |

---

## Monitoring & Maintenance

### View Services

```bash
docker-compose ps
docker-compose logs -f
```

### Backup Database

```bash
bash backup.sh
```

### Setup Automated Backups

```bash
crontab -e

# Add this line for daily backup at 2 AM
0 2 * * * cd /home/user/atlantiplex/hostinger-deployment && bash backup.sh
```

### SSL Certificate Auto-Renewal

```bash
crontab -e

# Add this line to renew 30 days before expiration
0 0 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /home/user/atlantiplex/hostinger-deployment/nginx/ssl/atlantiplex.crt && cp /etc/letsencrypt/live/your-domain.com/privkey.pem /home/user/atlantiplex/hostinger-deployment/nginx/ssl/atlantiplex.key && docker-compose -f /home/user/atlantiplex/hostinger-deployment/docker-compose.yml restart nginx
```

---

## URLs After Deployment

```
Website:  https://www.your-domain.com
Studio:   https://studio.your-domain.com
API:      https://api.your-domain.com
```

---

## Troubleshooting

### Services won't start
```bash
docker-compose logs
# Check .env variables and disk space
```

### SSL errors
```bash
openssl x509 -in nginx/ssl/atlantiplex.crt -text -noout
# Verify cert dates and paths
```

### Connection refused
```bash
docker-compose ps  # Check all running
netstat -tulpn | grep LISTEN  # Check ports
```

### Database issues
```bash
docker-compose exec postgres psql -U atlantiplex
# Test connection and check logs
```

---

## Production Checklist

- [ ] Domain registered and DNS configured
- [ ] SSH access to Hostinger VPS verified
- [ ] Docker and Docker Compose installed on VPS
- [ ] SSL certificates generated (Let's Encrypt)
- [ ] .env configured with all required values
- [ ] Nginx config updated with domain names
- [ ] Initial deployment successful
- [ ] All services healthy (docker-compose ps)
- [ ] Websites accessible in browser
- [ ] Database backups automated (crontab)
- [ ] SSL renewal automated (crontab)
- [ ] Monitoring/alerts configured

---

## Support & Documentation

- **Hostinger Setup:** `hostinger-deployment/README.md`
- **Kubernetes Setup:** `k8s-optimized/README.md`
- **Docker Optimization:** `DOCKERFILE_OPTIMIZATION_COMPLETE.md`
- **Quick Reference:** `hostinger-deployment/QUICK_REFERENCE.md`

---

**Ready to deploy!** Choose your option above and follow the steps.
