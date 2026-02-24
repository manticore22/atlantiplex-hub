# 🚀 Launch in 30 Minutes - Quick Start

**Atlantiplex Studio** - Matrix Broadcasting Platform

*Where theater meets technology, mystery meets broadcast*

**Total Time**: 30 minutes | **Complexity**: Medium | **Checklist**: [✓ Complete]

---

## ⚡ TL;DR - 3 Step Deployment

```bash
# Step 1: Setup VPS (10 min, one-time)
ssh root@YOUR_VPS_IP 'bash -s' < setup-hostinger.sh

# Step 2: Configure & Build (10 min)
cp .env.production.template .env.production
# Edit .env.production with real values
docker-compose build

# Step 3: Deploy (5 min)
./deploy-hostinger.sh production latest
```

**That's it. You're live.**

---

## 📋 Pre-Flight Checklist (5 minutes)

✅ = Done, ❌ = Fix, ⏳ = In Progress

```
ESSENTIAL (Must Have)
❌ [ ] Hostinger VPS provisioned (8GB RAM)
❌ [ ] SSH access working
❌ [ ] Domain registered
❌ [ ] Stripe keys obtained
❌ [ ] Email provider configured

SECURITY (Mandatory)
❌ [ ] Strong DB password generated (32+ chars)
❌ [ ] JWT secrets generated (openssl rand -hex 32)
❌ [ ] .env.production created (NEVER commit)
❌ [ ] API keys stored in secure vault
```

---

## 🔧 Setup (10 Minutes)

### 1️⃣ Provision Hostinger VPS
- Visit hostinger.com → Choose Business VPS (8GB RAM)
- Get: IP address, username, port
- Test SSH: `ssh root@YOUR_IP`

### 2️⃣ Run Automated Setup
```bash
ssh root@YOUR_VPS_IP 'bash -s' < setup-hostinger.sh
```

**What it does** (~10 min):
- Updates system
- Installs Docker & Compose
- Sets up firewall
- Configures SSL (Let's Encrypt)
- Creates backups & monitoring

**When done**: You'll see ✅ Hostinger VPS Setup Complete

---

## 🏗️ Build (10 Minutes)

### 1️⃣ Create Environment File
```bash
cp .env.production.template .env.production
nano .env.production

# Replace all CHANGE_ME values:
DB_PASSWORD=your_strong_password_here          # 32+ chars
REDIS_PASSWORD=your_redis_password              # 32+ chars
JWT_SECRET=your_jwt_secret                      # 32+ chars
STRIPE_SECRET_KEY=sk_live_YOUR_KEY
VITE_API_URL=https://your-domain.com
```

### 2️⃣ Build Docker Images
```bash
docker-compose build
```

**Output**: 3 images built successfully

### 3️⃣ Scan for Vulnerabilities (Optional but Recommended)
```bash
docker scout cves atlantiplex-stage:latest
docker scout cves atlantiplex-flask:latest
```

**Expected**: ✅ No critical/high CVEs

---

## 🚀 Deploy (5 Minutes)

### 1️⃣ Push to Registry
```bash
docker login
docker tag atlantiplex-stage:latest yourusername/atlantiplex-stage:latest
docker push yourusername/atlantiplex-stage:latest
docker push yourusername/atlantiplex-flask:latest
docker push yourusername/atlantiplex-frontend:latest
```

### 2️⃣ Deploy to Production
```bash
./deploy-hostinger.sh production latest
```

**What happens automatically**:
1. Backs up database
2. Pulls latest images
3. Stops old containers
4. Starts new services
5. Runs health checks
6. Verifies endpoints

### 3️⃣ Verify It Works
```bash
# SSH into server
ssh root@YOUR_VPS_IP

# Check services
cd /home/atlantiplex && docker-compose ps

# Test endpoints
curl http://localhost:9001/health
curl http://localhost:5000/api/health
curl http://localhost/health
```

**Expected**: All return 200 OK ✅

---

## 🌐 Domain & DNS (5-10 Minutes Setup + 24-48h Propagation)

### In DNS Registrar Settings:
```
A Record: your-domain.com      → YOUR_VPS_IP
A Record: www.your-domain.com  → YOUR_VPS_IP
```

### Verify Propagation (Wait 24-48 hours)
```bash
nslookup your-domain.com
# Should return: YOUR_VPS_IP
```

### SSL Certificate (Automated)
```bash
# Setup script already configured Let's Encrypt
# Certificate auto-renews yearly
# HTTPS works automatically
```

---

## ✅ Validation Checklist (5 Minutes)

After deployment, verify all items:

```bash
# 1. Services Running
docker-compose ps
# Expected: all "Up"

# 2. Health Endpoints
curl -s http://localhost:9001/health | jq .
curl -s http://localhost:5000/api/health | jq .
curl -s http://localhost/health

# 3. Database Connected
docker exec atlantiplex-postgres pg_isready -U atlantiplex

# 4. Redis Connected
docker exec atlantiplex-redis redis-cli ping
# Expected: PONG

# 5. No Error Logs
docker-compose logs --tail 20 | grep -i error
# Expected: No critical errors

# 6. Disk Space
df -h /home/atlantiplex
# Expected: >50GB available

# 7. Memory OK
docker stats --no-stream
# Expected: All services <80% memory
```

---

## 🔄 Rollback (If Something Goes Wrong)

```bash
# ONE command to go back
./deploy-hostinger.sh rollback

# Or manually
ssh root@YOUR_VPS_IP
cd /home/atlantiplex
docker-compose down
git checkout HEAD~1
docker-compose up -d
```

---

## 📊 Key Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Uptime | 99.5%+ | ⏳ |
| Response Time (p95) | <500ms | ⏳ |
| Error Rate | <0.1% | ⏳ |
| CPU Usage | <70% | ⏳ |
| Memory Usage | <80% | ⏳ |
| Database Load | <70% | ⏳ |

Monitor these real-time:
```bash
# On server
docker stats
```

---

## 🆘 Quick Troubleshooting

### Service Won't Start
```bash
ssh root@YOUR_VPS_IP
cd /home/atlantiplex
docker-compose logs atlantiplex-flask
# Look for error message
```

### High Memory Usage
```bash
docker stats
# Identify container
docker restart atlantiplex-flask
```

### Database Error
```bash
docker logs atlantiplex-postgres | tail -20
docker-compose restart atlantiplex-postgres
```

### Can't Access Domain
```bash
# Wait 24-48 hours for DNS
nslookup your-domain.com

# Check firewall
ssh root@YOUR_VPS_IP
ufw status
```

### Port Already in Use
```bash
ssh root@YOUR_VPS_IP
lsof -i :80
lsof -i :443
# Kill process if needed: kill -9 <PID>
```

---

## 📱 Monitoring (Ongoing)

### Daily
```bash
# SSH into server
docker-compose ps                # Check all running
docker stats --no-stream         # Check resources
docker-compose logs | tail -20   # Check errors
```

### Weekly
```bash
# Performance
docker exec atlantiplex-postgres psql -U atlantiplex -d atlantiplex \
  -c "SELECT * FROM pg_stat_statements LIMIT 10;"

# Backups
ls -lh /home/atlantiplex/backups/
```

### Monthly
```bash
# Security scan
docker scout cves atlantiplex-stage:latest

# Disk space
df -h

# Optimize database
docker exec atlantiplex-postgres reindexdb -U atlantiplex atlantiplex
```

---

## 🔐 Security After Launch

### Weekly
- [ ] Check for new CVEs: `docker scout cves <image>`
- [ ] Review logs for suspicious activity

### Monthly
- [ ] Rotate database password
- [ ] Rotate API keys
- [ ] Update Docker images

### Quarterly
- [ ] Full security audit
- [ ] Penetration testing
- [ ] Access control review

---

## 📞 Emergency Contacts

| Issue | Action |
|-------|--------|
| Services Down | `docker-compose restart` |
| Database Error | `docker logs atlantiplex-postgres` |
| High CPU/Memory | `docker stats` + scale or restart |
| SSL Certificate | Auto-renews, usually no action needed |
| Hostinger Support | https://www.hostinger.com/help |

---

## ✨ Success = All Green

```
✅ All services running (docker-compose ps)
✅ Health endpoints responding (curl /health)
✅ Database connected (pg_isready)
✅ Redis connected (redis-cli ping)
✅ No critical errors (docker logs)
✅ Disk space available (df -h)
✅ SSL working (https://your-domain.com)
✅ Users can access (check your-domain.com)
```

---

## 📚 Full Documentation

If you need details beyond this quick start:

- **Setup Issues?** → See HOSTINGER_DEPLOYMENT_GUIDE.md
- **Pre-Launch Tasks?** → See PRE_LAUNCH_CHECKLIST.md
- **Security Concerns?** → See VULNERABILITY_REMEDIATION.md
- **Performance?** → See BEFORE_AFTER_METRICS.md
- **Commands?** → See QUICK_REFERENCE.md

---

**Estimated Total Time**: 30 minutes
**Go-Live Time**: 5-10 minutes after deployment
**DNS Propagation**: 24-48 hours for worldwide access

**Status**: ✅ Ready to launch

Good luck! 🎉
