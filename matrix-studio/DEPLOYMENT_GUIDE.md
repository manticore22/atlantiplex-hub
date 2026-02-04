# Oracle Cloud Deployment Guide
# Deploy Atlantiplex Matrix Studio to verilysovereign.org

## 🚀 Quick Deployment

### 1. Create Oracle Cloud Instance
1. Sign up for [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
2. Create a compute instance (Ampere A1 core - Free Tier eligible)
3. Choose Ubuntu 22.04 as OS
4. Assign public IP address
5. Configure security group to allow: 22 (SSH), 80 (HTTP), 443 (HTTPS)

### 2. Connect to Your Instance
```bash
ssh -i path/to/your-key.pem ubuntu@your-public-ip
```

### 3. Run Deployment Script
```bash
# Clone your repository (replace with your actual repo)
git clone https://github.com/yourusername/matrix-studio.git
cd matrix-studio

# Make deployment script executable
chmod +x deploy-oracle-cloud.sh

# Run deployment (update email in script first)
./deploy-oracle-cloud.sh
```

### 4. Configure DNS
1. Go to your domain registrar (Namecheap, GoDaddy, etc.)
2. Point `verilysovereign.org` and `www.verilysovereign.org` to your Oracle Cloud public IP
3. Wait for DNS propagation (usually 15-30 minutes)

## 🔧 Manual Setup Steps

If you prefer manual deployment:

### 1. System Setup
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. Configure Firewall
```bash
sudo ufw --force enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### 4. Setup Application
```bash
# Clone repository
git clone https://github.com/yourusername/matrix-studio.git
cd matrix-studio

# Setup environment
cp .env.production .env
# Edit .env with your actual values

# Create directories
mkdir -p certbot/conf certbot/www logs/nginx uploads
```

### 5. Start SSL Certificate Generation
```bash
# Start temporary nginx
docker-compose up -d nginx

# Generate SSL certificates
docker-compose run --rm certbot

# Stop temporary services
docker-compose down
```

### 6. Deploy Application
```bash
docker-compose up -d --build
```

## 📱 Access Your Application

After deployment:
- **Main Application**: https://verilysovereign.org
- **API Documentation**: https://verilysovereign.org/api
- **Health Check**: https://verilysovereign.org/api/health

## 🔐 Default Credentials
- Username: `demo`
- Password: `demo123`

## 🛠️ Management Commands

```bash
# View logs
docker-compose logs -f

# Stop application
docker-compose down

# Restart application
docker-compose restart

# Update application
git pull origin main
docker-compose up -d --build

# Check status
docker-compose ps
```

## 🔄 SSL Certificate Auto-Renewal

SSL certificates are automatically renewed monthly via cron job. To check:
```bash
crontab -l
```

## 🔧 Troubleshooting

### Common Issues:

1. **Permission Denied**: 
   ```bash
   sudo chown -R $USER:$USER uploads logs certbot
   ```

2. **Port Already in Use**:
   ```bash
   sudo lsof -i :80
   sudo lsof -i :443
   ```

3. **Docker Issues**:
   ```bash
   sudo systemctl restart docker
   ```

4. **SSL Certificate Issues**:
   ```bash
   docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email your-email@verilysovereign.org --agree-tos --no-eff-email -d verilysovereign.org -d www.verilysovereign.org --force-renewal
   ```

## 📊 Monitoring

Monitor your application:
```bash
# Check application health
curl https://verilysovereign.org/api/health

# View resource usage
docker stats
```

## 🚨 Security Recommendations

1. Change default passwords immediately
2. Update `.env` with strong secret keys
3. Regularly update the system: `sudo apt update && sudo apt upgrade`
4. Monitor logs for suspicious activity
5. Backup your data regularly

## 📞 Support

If you encounter issues:
1. Check logs: `docker-compose logs`
2. Verify all environment variables are set correctly
3. Ensure DNS is pointing to your Oracle Cloud instance
4. Check firewall settings
5. Verify SSL certificates are valid