#!/bin/bash

################################################################################
# Atlantiplex Studio - Hostinger VPS Initial Setup
# Purpose: Configure Hostinger VPS for Docker deployment
# Usage: ssh root@your-vps.hostinger.com 'bash -s' < setup-hostinger.sh
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

APP_USER="atlantiplex"
APP_DIR="/home/atlantiplex"

################################################################################
# Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

################################################################################
# System Updates
################################################################################

update_system() {
    log_info "Updating system packages..."
    apt-get update
    apt-get upgrade -y
    apt-get install -y \
        curl \
        wget \
        git \
        vim \
        htop \
        net-tools \
        ufw \
        fail2ban \
        certbot \
        python3-certbot-nginx \
        jq \
        unzip
    
    log_success "System packages updated"
}

################################################################################
# Docker Installation
################################################################################

install_docker() {
    log_info "Installing Docker..."
    
    if command -v docker &> /dev/null; then
        log_success "Docker already installed"
        return
    fi
    
    # Add Docker GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
    
    # Add Docker repository
    apt-get install -y software-properties-common
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    
    # Install Docker
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Start Docker
    systemctl enable docker
    systemctl start docker
    
    log_success "Docker installed"
}

install_docker_compose() {
    log_info "Installing Docker Compose..."
    
    DOCKER_COMPOSE_VERSION="v2.24.0"
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    log_success "Docker Compose installed"
}

################################################################################
# Application User Setup
################################################################################

setup_app_user() {
    log_info "Setting up application user..."
    
    if id "$APP_USER" &>/dev/null; then
        log_success "User $APP_USER already exists"
        return
    fi
    
    # Create user
    useradd -m -s /bin/bash "$APP_USER"
    
    # Add to docker group
    usermod -aG docker "$APP_USER"
    
    # Create necessary directories
    sudo -u "$APP_USER" mkdir -p "$APP_DIR"
    sudo -u "$APP_USER" mkdir -p "$APP_DIR/backups"
    sudo -u "$APP_USER" mkdir -p "$APP_DIR/data"
    sudo -u "$APP_USER" mkdir -p "$APP_DIR/logs"
    
    log_success "Application user setup completed"
}

################################################################################
# Firewall Configuration
################################################################################

setup_firewall() {
    log_info "Configuring firewall..."
    
    # Enable UFW
    ufw --force enable
    
    # Allow SSH
    ufw allow 22/tcp
    
    # Allow HTTP/HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Allow Docker
    ufw allow from 172.17.0.0/16 to any port 443
    
    # Block everything else by default
    ufw default deny incoming
    ufw default allow outgoing
    
    log_success "Firewall configured"
}

################################################################################
# SSL Certificate
################################################################################

setup_ssl() {
    log_info "Setting up SSL certificate..."
    
    read -p "Enter your domain name (e.g., example.com): " DOMAIN
    read -p "Enter your email for Let's Encrypt: " EMAIL
    
    # Create nginx config for certbot
    mkdir -p /etc/nginx/sites-available
    
    cat > /etc/nginx/sites-available/default << 'EOF'
server {
    listen 80;
    server_name _;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
}
EOF
    
    # Start nginx temporarily
    docker run -d --name certbot-nginx \
        -p 80:80 \
        -v /var/www/certbot:/var/www/certbot \
        -v /etc/letsencrypt:/etc/letsencrypt \
        nginx:latest
    
    # Get certificate
    certbot certonly --standalone -d "$DOMAIN" -d "www.$DOMAIN" --email "$EMAIL" --agree-tos --no-eff-email
    
    # Stop nginx
    docker stop certbot-nginx
    docker rm certbot-nginx
    
    # Set up auto-renewal
    cat > /etc/cron.daily/renew-ssl << 'EOF'
#!/bin/bash
certbot renew --quiet
EOF
    
    chmod +x /etc/cron.daily/renew-ssl
    
    log_success "SSL certificate setup completed"
}

################################################################################
# Nginx Configuration
################################################################################

setup_nginx() {
    log_info "Setting up Nginx reverse proxy..."
    
    read -p "Enter your domain name: " DOMAIN
    
    cat > /home/atlantiplex/nginx.conf << 'NGINX_CONF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 2048;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 20M;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;
    
    # Upstream services
    upstream stage_server {
        server stage-server:9001;
    }
    
    upstream flask_backend {
        server flask-backend:5000;
    }
    
    # HTTP redirect to HTTPS
    server {
        listen 80;
        server_name _;
        
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        location / {
            return 301 https://$host$request_uri;
        }
    }
    
    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name _;
        
        # SSL certificates
        ssl_certificate /etc/letsencrypt/live/YOUR_DOMAIN/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/YOUR_DOMAIN/privkey.pem;
        
        # SSL configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        
        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        
        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
        
        # API proxying
        location /api/stage/ {
            limit_req zone=api burst=100 nodelay;
            proxy_pass http://stage_server/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        location /api/flask/ {
            limit_req zone=api burst=100 nodelay;
            proxy_pass http://flask_backend/;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Frontend
        location / {
            limit_req zone=general burst=20 nodelay;
            proxy_pass http://frontend_server/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
NGINX_CONF
    
    log_success "Nginx configuration created"
}

################################################################################
# Monitoring Setup
################################################################################

setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Create health check script
    cat > /home/atlantiplex/health-check.sh << 'HEALTH_CHECK'
#!/bin/bash
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="/home/atlantiplex/health-check.log"

# Check Docker
if ! pgrep -x "dockerd" > /dev/null; then
    echo "[$TIMESTAMP] ERROR: Docker daemon not running" >> "$LOG_FILE"
    systemctl restart docker
fi

# Check containers
RUNNING=$(docker ps --format '{{.Names}}' | wc -l)
echo "[$TIMESTAMP] Running containers: $RUNNING" >> "$LOG_FILE"

# Check disk space
DISK_USAGE=$(df /home/atlantiplex | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "[$TIMESTAMP] WARNING: Disk usage at $DISK_USAGE%" >> "$LOG_FILE"
fi

# Check memory
MEMORY_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
echo "[$TIMESTAMP] Memory usage: $MEMORY_USAGE%" >> "$LOG_FILE"

# Health endpoints
curl -s http://localhost:9001/health > /dev/null 2>&1 || echo "[$TIMESTAMP] ERROR: Stage server unhealthy" >> "$LOG_FILE"
curl -s http://localhost:5000/api/health > /dev/null 2>&1 || echo "[$TIMESTAMP] ERROR: Flask backend unhealthy" >> "$LOG_FILE"
HEALTH_CHECK
    
    chmod +x /home/atlantiplex/health-check.sh
    chown atlantiplex:atlantiplex /home/atlantiplex/health-check.sh
    
    # Add to crontab
    (sudo -u atlantiplex crontab -l 2>/dev/null || echo ""; echo "*/5 * * * * /home/atlantiplex/health-check.sh") | sudo -u atlantiplex crontab -
    
    log_success "Monitoring setup completed"
}

################################################################################
# Backup Configuration
################################################################################

setup_backups() {
    log_info "Setting up automated backups..."
    
    # Create backup script
    cat > /home/atlantiplex/backup.sh << 'BACKUP_SCRIPT'
#!/bin/bash
BACKUP_DIR="/home/atlantiplex/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Database backup
docker exec atlantiplex-postgres pg_dump -U atlantiplex atlantiplex | gzip > "$BACKUP_DIR/postgres_$TIMESTAMP.sql.gz"

# Application data backup
tar -czf "$BACKUP_DIR/data_$TIMESTAMP.tar.gz" /home/atlantiplex/data/

# Clean old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed at $TIMESTAMP" >> "$BACKUP_DIR/backup.log"
BACKUP_SCRIPT
    
    chmod +x /home/atlantiplex/backup.sh
    chown atlantiplex:atlantiplex /home/atlantiplex/backup.sh
    
    # Schedule daily backup at 2 AM
    (sudo -u atlantiplex crontab -l 2>/dev/null || echo ""; echo "0 2 * * * /home/atlantiplex/backup.sh") | sudo -u atlantiplex crontab -
    
    log_success "Backup configuration completed"
}

################################################################################
# Main Setup Flow
################################################################################

main() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Atlantiplex Studio - Hostinger VPS Setup${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    update_system
    install_docker
    install_docker_compose
    setup_app_user
    setup_firewall
    setup_nginx
    setup_ssl
    setup_monitoring
    setup_backups
    
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Hostinger VPS Setup Completed!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run: ./deploy-hostinger.sh production latest"
    echo "2. Configure domain DNS to point to this server"
    echo "3. Monitor application at https://your-domain.com/health"
    echo ""
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
   log_error "This script must be run as root"
fi

main
