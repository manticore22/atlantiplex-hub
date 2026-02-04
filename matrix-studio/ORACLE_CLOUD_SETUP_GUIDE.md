# 🚀 Oracle Cloud Setup Guide for Atlantiplex Matrix Studio
# Step-by-step account creation and deployment

## 📋 **Prerequisites**
- Email address (for account verification)
- Credit card (for free tier verification, no charges unless you exceed limits)
- Computer with internet access
- 15-30 minutes for setup

## 🔧 **Step 1: Create Oracle Cloud Account**

### 1A. Go to Oracle Cloud
```
https://www.oracle.com/cloud/free/
```

### 1B. Sign Up
1. Click **"Start for Free"** or **"Sign Up"**
2. Choose **"Personal Account"**
3. Enter your email address
4. Create password
5. Provide personal details:
   - Full name
   - Country/Region
   - Phone number

### 1C. Email Verification
1. Check your email for verification code
2. Enter code on Oracle website
3. Verify your phone number (SMS code)

### 1D. Payment Information
1. Enter credit card details (required for free tier verification)
2. **NOTE**: You won't be charged unless you exceed free limits
3. Accept terms and conditions
4. Complete account setup

## 💰 **Free Tier Benefits You Get**
- **Compute**: 4 AMD-based CPUs, 24 GB RAM
- **Storage**: 200 GB block storage
- **Bandwidth**: 10 TB outbound data transfer
- **Load Balancer**: 1 load balancer
- **Databases**: 2 autonomous databases
- **Monitoring**: 500 million monitoring datapoints
- **Notifications**: 1 million delivery per month
- **Always Free**: Never expires as long as you use it

## 🏗️ **Step 2: Set Up Your First Instance**

### 2A. Log into Cloud Console
```
https://console.oracle-cloud.com/
```

### 2B. Navigate to Compute
1. Click **☰** menu (top left)
2. Go to **"Compute"** → **"Instances"**
3. Select your **Compartment** (usually root compartment)

### 2C. Create Compute Instance
1. Click **"Create Instance"**
2. Fill in the details:

**Instance Details:**
- **Name**: `matrix-studio-server`
- **Availability Domain**: Choose default
- **Image**: 
  - Click **"Change Image"**
  - Select **"Ubuntu"** → **"Ubuntu 22.04"** 
  - Click **"Select Image"**
- **Shape**:
  - Click **"Change Shape"**
  - Select **"VM.Standard.A1.Flex"** (Ampere A1 - Free Tier Eligible)
  - Set **"OCPUs"**: 2 (within free tier)
  - Set **"Memory (GB)"**: 8 (within free tier)
  - Click **"Select Shape"**

### 2D. Networking
1. **Virtual Cloud Network**: Click **"Create VCN"**
   - Name: `matrix-studio-vcn`
   - CIDR Block: `10.0.0.0/16`
   - Leave other defaults
   - Click **"Create"**

2. **Subnet**: Click **"Create Subnet"**
   - Name: `public-subnet`
   - CIDR Block: `10.0.1.0/24`
   - Access Type: **"Public"**
   - Click **"Create"**

3. **Public IP**: Keep **"Assign a public IP address"** checked

### 2E. SSH Keys
1. **Download Private Key**: Click **"Download Private Key"**
   - Save as: `oracle-key.pem`
   - **IMPORTANT**: Keep this file secure!

2. Or **Upload Your Own SSH Key** (if you have one)

### 2F. Final Steps
1. Leave other settings as default
2. Click **"Create Instance"**
3. Wait 2-5 minutes for instance to be created

## 🔐 **Step 3: Connect to Your Instance**

### 3A. Find Your Instance Details
1. In **Instances** page, click on your instance name
2. Copy the **Public IP Address** (e.g., `123.45.67.89`)
3. Note the **Username**: `ubuntu`

### 3B. Set Up SSH Access

**On Windows:**
1. Open **PowerShell** or **Command Prompt**
2. Navigate to where you saved the key:
   ```powershell
   cd Downloads
   ```
3. Set proper permissions:
   ```powershell
   icacls oracle-key.pem /grant "NT AUTHORITY\Authenticated Users:(R)"
   ```
4. Connect:
   ```powershell
   ssh -i oracle-key.pem ubuntu@123.45.67.89
   ```
   *(Replace 123.45.67.89 with your actual Public IP)*

**On Mac/Linux:**
1. Open Terminal
2. Navigate to key location:
   ```bash
   cd Downloads
   ```
3. Set proper permissions:
   ```bash
   chmod 400 oracle-key.pem
   ```
4. Connect:
   ```bash
   ssh -i oracle-key.pem ubuntu@123.45.67.89
   ```

### 3C. First Connection
1. Accept the fingerprint (type `yes`)
2. You're now connected to your Oracle Cloud instance!

## 🛠️ **Step 4: Install Matrix Studio**

### 4A. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 4B. Install Required Software
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo apt install git -y
```

### 4C. Clone Your Matrix Studio Repository
```bash
# Log out and back in for Docker group
exit
# Connect again
ssh -i oracle-key.pem ubuntu@123.45.67.89

# Clone repository (replace with your actual repo)
git clone https://github.com/yourusername/matrix-studio.git
cd matrix-studio
```

### 4D. Set Up Environment
```bash
# Copy production environment
cp .env.production .env

# Edit with your actual values
nano .env
```

**Edit these values in .env:**
```bash
# Domain Configuration
DOMAIN=verilysovereign.org
BASE_URL=https://verilysovereign.org

# Security (generate new secrets)
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this

# Stripe Configuration (get from stripe.com)
STRIPE_SECRET_KEY=sk_live_your_actual_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_actual_key  
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 🚀 **Step 5: Deploy Matrix Studio**

### 5A. Deploy with Docker Compose
```bash
# Build and start all services
docker-compose up -d --build

# Check status
docker-compose ps
```

### 5B. Verify Deployment
```bash
# Check application logs
docker-compose logs -f matrix-studio

# Check nginx logs
docker-compose logs -f nginx
```

### 5C. Test Application
1. **HTTP Access**: http://123.45.67.89 (should redirect to HTTPS)
2. **API Health**: http://123.45.67.89/api/health
3. **Login**: http://123.45.67.89 (manticore/patriot8812)

## 🌐 **Step 6: Configure Domain**

### 6A. Get Your IP Address
1. In Oracle Console, go to **Instances**
2. Copy your **Public IP Address**

### 6B. Update DNS at Namecheap
1. Log into Namecheap account
2. Go to **Domain List** → verilysovereign.org → **Manage**
3. Click **"Advanced DNS"**
4. Add these records:

```
Type: A Record
Name: @ (or verilysovereign.org)  
Value: YOUR_ORACLE_IP
TTL: Automatic

Type: A Record
Name: www
Value: YOUR_ORACLE_IP
TTL: Automatic
```

5. Save changes

### 6C. Wait for DNS Propagation
- Usually takes 15-30 minutes
- Check with: `ping verilysovereign.org`

## 🔒 **Step 7: Setup SSL Certificates**

### 7A. Configure SSL
1. Update `nginx.conf` with your domain
2. Let's Encrypt certificates are auto-generated
3. SSL renewal is automatic

### 7B. Test HTTPS
1. Access: https://verilysovereign.org
2. Check SSL certificate validity
3. Verify redirect from HTTP to HTTPS

## 📊 **Step 8: Monitor and Manage**

### 8A. Oracle Cloud Console
- **Instances**: Monitor server performance
- **Monitoring**: Check CPU, memory, network
- **Billing**: Track usage against free tier

### 8B. Application Monitoring
```bash
# View application logs
docker-compose logs -f

# Check server status
curl https://verilysovereign.org/api/health

# Monitor Docker containers
docker stats
```

## 💰 **Cost Management**

### Free Tier Limits (Monthly):
- **Compute**: 4 AMD CPUs, 24 GB RAM
- **Storage**: 200 GB block storage  
- **Bandwidth**: 10 TB outbound data
- **Load Balancer**: 1 load balancer

### Monitor Usage:
1. Oracle Console → Billing → Cost Analysis
2. Set up billing alerts
3. Monitor against free tier limits

## 🔧 **Troubleshooting**

### Common Issues:

**SSH Connection Failed:**
```bash
# Check permissions
chmod 400 oracle-key.pem

# Try with verbose output
ssh -v -i oracle-key.pem ubuntu@123.45.67.89
```

**Docker Not Running:**
```bash
# Start Docker
sudo systemctl start docker

# Add user to Docker group
sudo usermod -aG docker ubuntu
# Logout and login again
```

**Application Not Accessible:**
```bash
# Check nginx status
docker-compose ps

# Check ports
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# Check firewall
sudo ufw status
```

## 🎯 **Success Metrics**

Once completed, you'll have:
- ✅ **Live Matrix Studio** at verilysovereign.org
- ✅ **SSL Certificate** automatically configured
- ✅ **Payment Processing** via Stripe
- ✅ **Admin Access** with manticore/patriot8812
- ✅ **Free Hosting** on Oracle Cloud
- ✅ **Professional Platform** ready for monetization

## 📞 **Support Resources**

- **Oracle Support**: https://cloud.oracle.com/support
- **Documentation**: https://docs.oracle.com/en/cloud/
- **Community**: https://community.oracle.com/

Your Matrix Studio will be running on enterprise-grade infrastructure with zero hosting costs (within free tier)! 🚀