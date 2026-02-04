# 🚀 Google Cloud Melbourne Deployment Guide
# Step-by-step setup for Matrix Studio: 2 vCPU, 4GB RAM, $15-18/month

## 🎯 **Target Configuration**
- **Cost**: $15-18/month (within your $20 budget)
- **Specs**: 2 vCPU, 4GB RAM, 50GB SSD
- **Region**: Melbourne (australia-southeast1)
- **Latency**: 15-25ms from Adelaide (Excellent!)
- **Bonus**: $300 free credits first 90 days

---

## 📋 **Before You Start**

### **What You Need:**
1. ✅ **Email address** for account creation
2. ✅ **Credit card** (for verification, won't be charged unless you exceed credits)
3. ✅ **30 minutes** for setup time
4. ✅ **Matrix Studio code** ready

### **What You'll Get:**
- 🚀 **Professional hosting** with enterprise infrastructure
- 💰 **$300 free credits** (first 90 days)
- 📍 **Melbourne region** (best for Adelaide users)
- 🛡️ **Enterprise security** and reliability
- 🌐 **Global CDN** included

---

## 🚀 **Step 1: Create Google Cloud Account**

### **1A. Sign Up**
1. Go to: https://console.cloud.google.com/free
2. Click **"Create account"**
3. Choose **"Personal account"**
4. Fill in:
   - **Email**: your-email@gmail.com
   - **Password**: create strong password
   - **Country**: Australia
   - **Full name**: Your details
5. **Add payment method** (credit card for verification)
6. **Verify email** (check your inbox)
7. **Verify phone** (SMS code)

### **1B. Verify Free Credits**
1. After signup, check: https://console.cloud.google.com/billing
2. You should see **"$300 in free credits"**
3. **Credits expire**: 90 days from signup

---

## 🏗️ **Step 2: Create Melbourne VM Instance**

### **2A. Navigate to Compute Engine**
1. In Google Cloud Console, click ☰ (top left)
2. Go to **"Compute Engine"** → **"VM instances"**
3. Click **"Create instance"**

### **2B. Configure Instance Details**

**Basic Information:**
```
Name: matrix-studio-prod
Region: australia-southeast1 (Melbourne)
Zone: australia-southeast1-a (or a/b/c - any works)
```

**Machine Configuration:**
```
Machine type: E2 series
Machine type: e2-medium (2 vCPU, 4GB RAM)
CPU platform: Intel Skylake
```

**Boot Disk:**
```
Boot disk type: Standard persistent disk
Size (GB): 50
Type: pd-standard
```

**Operating System:**
```
Image: Ubuntu
Version: Ubuntu 22.04 LTS
Size: 10 GB
```

**Firewall:**
```
Allow HTTP traffic: ✅ (checked)
Allow HTTPS traffic: ✅ (checked)
Allow SMTP traffic: ❌ (unchecked)
Network tags: http-server, https-server
```

**Advanced Options:**
```
Preemptibility: Off (for production)
Maintenance window: Any
Deletion protection: ✅ (prevent accidental deletion)
```

### **2C. Create Instance**
1. Click **"Create"**
2. Wait 2-3 minutes for instance to be ready
3. Note the **External IP address** (you'll need this later)

---

## 🔧 **Step 3: Connect to Your Instance**

### **3A. Using Google Cloud Shell (Easiest)**
1. In the console, click the **terminal icon** (🖥) top right
2. Wait for SSH connection to establish
3. You're now connected to your Melbourne instance!

### **3B. Using SSH Client (Advanced)**
```bash
# Method 1: gcloud CLI
gcloud compute ssh matrix-studio-prod

# Method 2: Traditional SSH
ssh -i ~/.ssh/google_compute_engine matrix-studio-prod
```

### **3C. First Connection Test**
```bash
# Once connected, run:
sudo apt update && sudo apt upgrade -y
hostname
whoami
# You should see: root@matrix-studio-prod
```

---

## 🐳 **Step 4: Install Docker & Requirements**

### **4A. Install Docker**
```bash
# Update package lists
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to Docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo apt install -y git

# Install other essentials
sudo apt install -y curl wget unzip
```

### **4B. Verify Docker Installation**
```bash
# Test Docker
docker --version
docker-compose --version

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

---

## 📦 **Step 5: Deploy Matrix Studio**

### **5A. Clone Repository**
```bash
# Navigate to home directory
cd /home/$USER

# Clone your Matrix Studio repository
git clone https://github.com/yourusername/matrix-studio.git
cd matrix-studio

# If you don't have a repo yet, copy files locally
# We'll use the existing enhanced files
```

### **5B. Configure Environment**
```bash
# Copy production environment template
cp .env.production .env

# Edit environment file
nano .env
```

**Edit these values in .env:**
```bash
# Domain Configuration
DOMAIN=verilysovereign.org
BASE_URL=https://verilysovereign.org

# Security (generate new secrets)
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-too

# Stripe Configuration (get from stripe.com later)
STRIPE_SECRET_KEY=sk_live_your_actual_key_here
STRIPE_PUBLISHABLE_KEY=pk_live_your_actual_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Database
DATABASE_URL=sqlite:///matrix_studio.db

# Google Cloud specific
PROJECT_ID=$(gcloud config get-value project)
ZONE=australia-southeast1-a
```

### **5C. Deploy with Docker Compose**
```bash
# Build and start all services
docker-compose up -d --build

# Check deployment status
docker-compose ps

# View logs (if needed)
docker-compose logs -f
```

---

## 🌐 **Step 6: Configure Domain and SSL**

### **6A. Get Instance IP Address**
```bash
# Method 1: Via Console
# Look at VM instances page - External IP column

# Method 2: Via Command Line
gcloud compute instances describe matrix-studio-prod \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

### **6B. Update DNS at Namecheap**
1. Log into Namecheap account
2. Go to **Domain List** → verilysovereign.org → **Manage**
3. Click **"Advanced DNS"**
4. Add these records:

```
Record Type: A Record
Name: @ (or verilysovereign.org)
Value: YOUR_EXTERNAL_IP
TTL: Automatic

Record Type: A Record  
Name: www
Value: YOUR_EXTERNAL_IP
TTL: Automatic
```

5. Save changes

### **6C. Verify DNS Propagation**
```bash
# Test domain resolution
ping verilysovereign.org
nslookup verilysovereign.org
# Wait 15-30 minutes for propagation
```

---

## 🔒 **Step 7: Setup SSL with Let's Encrypt**

### **7A. Install Certbot**
```bash
# SSH back to your instance
ssh matrix-studio-prod

# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot certonly --standalone \
  -d verilysovereign.org \
  -d www.verilysovereign.org \
  --email your-email@verilysovereign.org \
  --agree-tos \
  --non-interactive
```

### **7B. Configure Nginx for SSL**
```bash
# Edit nginx configuration
sudo nano /etc/nginx/sites-available/default
```

**Add SSL configuration:**
```nginx
server {
    listen 443 ssl;
    server_name verilysovereign.org www.verilysovereign.org;
    
    ssl_certificate /etc/letsencrypt/live/verilysovereign.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/verilysovereign.org/privkey.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name verilysovereign.org www.verilysovereign.org;
    return 301 https://$server_name$request_uri;
}
```

### **7C. Restart Nginx**
```bash
# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

# Enable auto-start
sudo systemctl enable nginx
```

---

## 🔍 **Step 8: Verify Deployment**

### **8A. Test Application**
```bash
# Check if Matrix Studio is running
curl http://localhost:8081/api/health

# Check HTTPS access
curl https://verilysovereign.org/api/health

# Expected response:
{
    "status": "healthy",
    "timestamp": "2024-02-04T...",
    "features": {
        "stripe_payments": true,
        "admin_bypass": true,
        "subscriptions": true
    }
}
```

### **8B. Test Admin Login**
```bash
# Test admin bypass login
curl -X POST https://verilysovereign.org/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "manticore", "password": "patriot8812"}'

# Expected response: token + admin privileges
```

---

## 💰 **Step 9: Monitor Costs and Usage**

### **9A. Check Current Billing**
1. Go to: https://console.cloud.google.com/billing
2. Look at **"Cost breakdown"**
3. Your e2-medium should show: **$15.38/month**

### **9B. Monitor Free Credits**
1. Check remaining credits: https://console.cloud.google.com/billing/credits
2. **$300 - usage** = remaining credits
3. Credits valid for: 90 days from signup

### **9C. Set Budget Alerts**
1. Go to: https://console.cloud.google.com/billing/budgets
2. Create budget: **$20/month**
3. Set alerts: 50%, 90%, 100% of budget

---

## 📊 **Expected Monthly Costs Breakdown**

| Service | Monthly Cost | Description |
|----------|-------------|-------------|
| **Compute Engine** | $15.38 | e2-medium (2 vCPU, 4GB RAM) |
| **Persistent Disk** | $1.70 | 50GB SSD storage |
| **Network Egress** | $0-2 | First 1TB free, then $0.12/GB |
| **Load Balancer** | $0 (not needed initially) |
| **Total** | **$17-18** | Within your $20 budget! |

### **When Free Credits Expire (After 90 days):**
- **Switch to**: e2-micro (free tier) or e2-small ($5.15/month)
- **Maintain performance**: Use Spot instances for 50-80% savings
- **Total cost**: $0-15/month (still within budget!)

---

## 🛡️ **Step 10: Security and Maintenance**

### **10A. Basic Security Setup**
```bash
# Update system regularly
sudo apt update && sudo apt upgrade -y

# Configure firewall
sudo ufw enable
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw deny incoming
sudo ufw enable

# Install fail2ban
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
```

### **10B. Backup Strategy**
```bash
# Set up automated backups
gcloud compute images create matrix-studio-backup \
  --source-disk matrix-studio-prod \
  --description "Weekly backup"

# Schedule regular backups
crontab -e
# Add: 0 2 * * 0 /usr/local/bin/backup-script.sh
```

### **10C. Monitoring**
```bash
# Install monitoring
curl -sSO https://get.docker.com | sh
sudo systemctl start docker
sudo systemctl enable docker

# Monitor container health
docker-compose ps
docker stats --no-stream
```

---

## 🎯 **Optimization Tips for $20 Budget**

### **Cost Optimization:**
1. **Use Spot Instances**: 50-80% savings on compute
2. **Right-size Resources**: Don't overprovision RAM/CPU
3. **Use Preemptible VMs**: 60-80% savings for development
4. **Optimize Storage**: Delete unused disks
5. **Monitor Bandwidth**: Stay within 1TB free tier

### **Performance Optimization:**
1. **Use Melbourne Region**: Best latency for Adelaide users
2. **Enable Caching**: Use Google Cloud CDN
3. **Load Testing**: Monitor resource usage
4. **Optimize Images**: Use smaller base images
5. **Scale Smartly**: Add resources only when needed

---

## 🚨 **Troubleshooting Common Issues**

### **Issue: SSH Connection Failed**
```bash
# Check if VM is running
gcloud compute instances list

# Check external IP
gcloud compute instances describe matrix-studio-prod

# Try SSH with verbose output
ssh -v matrix-studio-prod
```

### **Issue: Application Not Accessible**
```bash
# Check if Docker is running
docker-compose ps

# Check nginx status
sudo systemctl status nginx

# Check port availability
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

### **Issue: High Costs**
```bash
# Check current usage
gcloud billing accounts list

# Set budget alerts
gcloud billing budgets create --display-name="Matrix-Studio-Budget" --budget-amount=20

# Use cost breakdown
gcloud billing accounts list
```

---

## 🎉 **Success Metrics**

Once completed, you'll have:
- ✅ **Professional hosting**: Enterprise Google Cloud infrastructure
- ✅ **Melbourne location**: 15-25ms from Adelaide
- ✅ **Within budget**: $15-18/month total cost
- ✅ **High availability**: 99.9%+ uptime SLA
- ✅ **Global CDN**: Fast content delivery worldwide
- ✅ **SSL Security**: Free Let's Encrypt certificates
- ✅ **Auto-scaling**: Easy upgrade/downgrade options

### **Performance from Adelaide:**
- ⭐ **Latency**: 15-25ms (Excellent!)
- ⭐ **Reliability**: 99.9%+ uptime
- ⭐ **Speed**: 2 vCPU, 4GB RAM, SSD storage

### **Cost Management:**
- 💰 **Predictable**: $15-18/month fixed
- 💰 **Free period**: First 90 days using $300 credits
- 💰 **Budget alerts**: Notifications before overages
- 💰 **Free tier fallback**: Options to reduce costs further

---

## 🎯 **You're Ready!**

**Your Matrix Studio is now live at:**
- **URL**: https://verilysovereign.org
- **Admin Access**: manticore / patriot8812
- **Cost**: $0 for first 90 days, then $15-18/month
- **Performance**: Enterprise-grade hosting in Melbourne

**This gives you professional Australian hosting within your $20 budget with excellent Adelaide performance!** 🚀

## 📞 **Next Steps & Support**

1. **Monitor usage** first week to ensure costs stay within budget
2. **Set up Stripe** when ready for payments
3. **Configure DNS** once propagation completes
4. **Test all features** of Matrix Studio
5. **Set up backups** and monitoring

**For Google Cloud support:**
- **Documentation**: https://cloud.google.com/docs
- **Community**: https://cloud.google.com/community
- **Support**: https://cloud.google.com/support

**Enjoy your professional Matrix Studio hosting in Melbourne!** 🎯