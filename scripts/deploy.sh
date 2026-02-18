#!/bin/bash
#
# Atlantiplex Studio - Bare Metal Deployment Script
# Run this on your VPS/Dedicated Server
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="atlantiplex"
DOMAIN="${DOMAIN:-yourdomain.com}"
EMAIL="${EMAIL:-admin@yourdomain.com}"
INSTALL_DIR="${INSTALL_DIR:-/opt/atlantiplex}"

# Logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
       log_error "This script must be run as root"
       exit 1
    fi
}

# Update system
update_system() {
    log_info "Updating system packages..."
    apt-get update
    apt-get upgrade -y
    log_success "System updated"
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."
    
    # Install required packages
    apt-get install -y \
        curl \
        wget \
        git \
        nginx \
        certbot \
        python3-certbot-nginx \
        postgresql \
        postgresql-contrib \
        redis-server \
        ufw \
        fail2ban \
        htop \
        ncdu
    
    # Install Node.js 20.x
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
    
    # Install Python 3.11 and pip
    apt-get install -y python3.11 python3.11-venv python3-pip
    
    # Install Docker
    if ! command -v docker &> /dev/null; then
        log_info "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        usermod -aG docker $SUDO_USER
        systemctl enable docker
        systemctl start docker
    fi
    
    # Install Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_info "Installing Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
    
    log_success "Dependencies installed"
}

# Setup firewall
setup_firewall() {
    log_info "Configuring firewall..."
    
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 9001/tcp
    ufw --force enable
    
    log_success "Firewall configured"
}

# Setup SSL with Let's Encrypt
setup_ssl() {
    log_info "Setting up SSL with Let's Encrypt..."
    
    certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --agree-tos -n -m $EMAIL
    
    # Copy certificates to nginx directory
    mkdir -p $INSTALL_DIR/nginx/ssl
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $INSTALL_DIR/nginx/ssl/
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $INSTALL_DIR/nginx/ssl/
    
    # Setup auto-renewal
    (crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet") | crontab -
    
    log_success "SSL configured"
}

# Clone repository
clone_repo() {
    log_info "Cloning repository..."
    
    if [ -d "$INSTALL_DIR" ]; then
        log_warning "Directory $INSTALL_DIR exists, updating..."
        cd $INSTALL_DIR
        git pull
    else
        git clone https://github.com/yourusername/atlantiplex-hub.git $INSTALL_DIR
        cd $INSTALL_DIR
    fi
    
    log_success "Repository cloned/updated"
}

# Create environment file
create_env() {
    log_info "Creating environment configuration..."
    
    if [ ! -f "$INSTALL_DIR/.env" ]; then
        cat > $INSTALL_DIR/.env << EOF
# Database
DB_USER=atlantiplex
DB_PASSWORD=$(openssl rand -base64 32)
DB_NAME=atlantiplex
DATABASE_URL=postgresql://atlantiplex:$(openssl rand -base64 32)@postgres:5432/atlantiplex

# JWT
JWT_SECRET=$(openssl rand -base64 64)

# Stripe (replace with your keys)
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here

# Application
CORS_ORIGIN=https://$DOMAIN
API_URL=https://$DOMAIN
NODE_ENV=production
FLASK_ENV=production

# Redis
REDIS_URL=redis://redis:6379

# Server
STAGE_PORT=9001
FLASK_PORT=5000
EOF
        log_success "Environment file created at $INSTALL_DIR/.env"
        log_warning "IMPORTANT: Edit $INSTALL_DIR/.env and add your Stripe keys!"
    else
        log_warning "Environment file already exists"
    fi
}

# Setup PostgreSQL
setup_postgres() {
    log_info "Setting up PostgreSQL..."
    
    systemctl start postgresql
    systemctl enable postgresql
    
    # Create database and user
    su - postgres -c "psql -c \"CREATE USER atlantiplex WITH PASSWORD '$(grep DB_PASSWORD $INSTALL_DIR/.env | cut -d= -f2)';\"" || true
    su - postgres -c "psql -c \"CREATE DATABASE atlantiplex OWNER atlantiplex;\"" || true
    su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE atlantiplex TO atlantiplex;\"" || true
    
    log_success "PostgreSQL configured"
}

# Setup Redis
setup_redis() {
    log_info "Setting up Redis..."
    
    systemctl start redis-server
    systemctl enable redis-server
    
    # Configure Redis for persistence
    sed -i 's/^# appendonly no/appendonly yes/' /etc/redis/redis.conf
    sed -i 's/^appendfsync .*$/appendfsync everysec/' /etc/redis/redis.conf
    
    systemctl restart redis-server
    
    log_success "Redis configured"
}

# Build and deploy
build_and_deploy() {
    log_info "Building and deploying application..."
    
    cd $INSTALL_DIR
    
    # Update nginx configuration with domain
    sed -i "s/YOUR_DOMAIN/$DOMAIN/g" nginx/sites-enabled/atlantiplex.conf
    
    # Build and start containers
    docker-compose -f docker-compose.yml build
    docker-compose -f docker-compose.yml up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 30
    
    # Run database migrations
    docker-compose exec flask-backend python -m flask db upgrade || true
    
    log_success "Application deployed"
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Create log rotation
    cat > /etc/logrotate.d/atlantiplex << EOF
$INSTALL_DIR/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF
    
    # Create monitoring script
    cat > /usr/local/bin/atlantiplex-health << 'EOF'
#!/bin/bash
# Health check script

if ! curl -f http://localhost:9001/health > /dev/null 2>&1; then
    echo "Stage server is down, restarting..."
    cd /opt/atlantiplex && docker-compose restart stage-server
fi

if ! curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "Flask backend is down, restarting..."
    cd /opt/atlantiplex && docker-compose restart flask-backend
fi
EOF
    chmod +x /usr/local/bin/atlantiplex-health
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/atlantiplex-health") | crontab -
    
    log_success "Monitoring configured"
}

# Main deployment function
deploy() {
    log_info "Starting Atlantiplex Studio deployment..."
    log_info "Target domain: $DOMAIN"
    log_info "Install directory: $INSTALL_DIR"
    
    check_root
    update_system
    install_dependencies
    setup_firewall
    clone_repo
    create_env
    setup_postgres
    setup_redis
    setup_ssl
    build_and_deploy
    setup_monitoring
    
    log_success "================================"
    log_success "Deployment Complete!"
    log_success "================================"
    log_info "Your application is now running at: https://$DOMAIN"
    log_info ""
    log_info "Next steps:"
    log_info "1. Edit $INSTALL_DIR/.env and add your Stripe API keys"
    log_info "2. Restart services: cd $INSTALL_DIR && docker-compose restart"
    log_info "3. Configure Stripe webhooks: https://$DOMAIN/api/webhooks/stripe"
    log_info ""
    log_info "Management commands:"
    log_info "  - View logs: cd $INSTALL_DIR && docker-compose logs -f"
    log_info "  - Restart: cd $INSTALL_DIR && docker-compose restart"
    log_info "  - Update: cd $INSTALL_DIR && git pull && docker-compose up -d --build"
    log_info ""
    log_info "Monitoring:"
    log_info "  - Health check runs every 5 minutes via cron"
    log_info "  - SSL certificates auto-renew via certbot"
}

# Display help
show_help() {
    cat << EOF
Atlantiplex Studio - Bare Metal Deployment Script

Usage: $0 [OPTIONS]

Options:
    -d, --domain DOMAIN     Set domain name (default: yourdomain.com)
    -e, --email EMAIL       Set admin email (default: admin@yourdomain.com)
    -i, --install-dir DIR   Set installation directory (default: /opt/atlantiplex)
    -h, --help             Show this help message

Environment Variables:
    DOMAIN                 Domain name
    EMAIL                  Admin email address
    INSTALL_DIR            Installation directory

Example:
    sudo DOMAIN=studio.example.com EMAIL=admin@example.com ./deploy.sh
    sudo ./deploy.sh --domain studio.example.com --email admin@example.com

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain)
            DOMAIN="$2"
            shift 2
            ;;
        -e|--email)
            EMAIL="$2"
            shift 2
            ;;
        -i|--install-dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run deployment
deploy
