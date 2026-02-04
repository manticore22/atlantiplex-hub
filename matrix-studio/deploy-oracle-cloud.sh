#!/bin/bash

# Oracle Cloud Deployment Script for Atlantiplex Matrix Studio
# Domain: verilysovereign.org

set -e

echo "🚀 Deploying Atlantiplex Matrix Studio to Oracle Cloud..."

# Configuration
DOMAIN="verilysovereign.org"
EMAIL="your-email@verilysovereign.org"  # Update this

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Oracle Cloud
check_oracle_cloud() {
    if curl -s http://169.254.169.254/opc/v1/instance/ | grep -q "oracle"; then
        print_status "Running on Oracle Cloud instance"
        return 0
    else
        print_warning "Not running on Oracle Cloud instance"
        return 1
    fi
}

# Update system
update_system() {
    print_status "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
}

# Install Docker
install_docker() {
    print_status "Installing Docker..."
    
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    
    # Install Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    rm get-docker.sh
    
    print_status "Docker installed successfully"
}

# Setup firewall
setup_firewall() {
    print_status "Configuring firewall..."
    
    sudo ufw --force enable
    sudo ufw allow 22/tcp    # SSH
    sudo ufw allow 80/tcp    # HTTP
    sudo ufw allow 443/tcp   # HTTPS
    sudo ufw status
}

# Clone repository (if needed)
setup_repository() {
    print_status "Setting up repository..."
    
    if [ ! -d "matrix-studio" ]; then
        # Replace with your actual repository URL
        git clone https://github.com/yourusername/matrix-studio.git
        cd matrix-studio
    else
        cd matrix-studio
        git pull origin main
    fi
}

# Setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Copy production environment file
    if [ ! -f ".env" ]; then
        cp .env.production .env
        print_warning "Please update .env with your actual configuration"
    fi
    
    # Create necessary directories
    mkdir -p certbot/conf certbot/www logs/nginx uploads
    
    # Set permissions
    sudo chown -R $USER:$USER uploads logs certbot
    chmod 755 uploads logs
}

# Generate SSL certificates
setup_ssl() {
    print_status "Setting up SSL certificates..."
    
    # Start temporary nginx for certbot validation
    docker-compose up -d nginx
    
    # Wait for nginx to start
    sleep 10
    
    # Request SSL certificate
    docker-compose run --rm certbot
    
    # Stop temporary services
    docker-compose down
    
    print_status "SSL certificates generated"
}

# Deploy application
deploy_application() {
    print_status "Deploying Matrix Studio..."
    
    # Build and start all services
    docker-compose up -d --build
    
    # Check if services are running
    sleep 30
    
    if docker-compose ps | grep -q "Up"; then
        print_status "✅ Matrix Studio deployed successfully!"
        print_status "Access your application at: https://$DOMAIN"
    else
        print_error "❌ Deployment failed. Check logs with 'docker-compose logs'"
        exit 1
    fi
}

# Setup auto-renewal for SSL certificates
setup_ssl_renewal() {
    print_status "Setting up SSL certificate auto-renewal..."
    
    # Create renewal script
    cat > renew-ssl.sh << 'EOF'
#!/bin/bash
cd /path/to/matrix-studio
docker-compose run --rm certbot renew
docker-compose exec nginx nginx -s reload
EOF
    
    # Make it executable
    chmod +x renew-ssl.sh
    
    # Add to crontab (renew at 3:00 AM on the 1st of every month)
    (crontab -l 2>/dev/null; echo "0 3 1 * * /path/to/matrix-studio/renew-ssl.sh") | crontab -
    
    print_status "SSL auto-renewal configured"
}

# Display deployment info
display_info() {
    print_status "🎉 Deployment Complete!"
    echo ""
    echo "📱 Application URLs:"
    echo "   • Main App: https://$DOMAIN"
    echo "   • API Docs: https://$DOMAIN/api"
    echo "   • Health Check: https://$DOMAIN/api/health"
    echo ""
    echo "🔐 Default Credentials:"
    echo "   • Username: demo"
    echo "   • Password: demo123"
    echo ""
    echo "🛠️ Management Commands:"
    echo "   • View logs: docker-compose logs -f"
    echo "   • Stop app: docker-compose down"
    echo "   • Restart app: docker-compose restart"
    echo "   • Update app: git pull && docker-compose up -d --build"
    echo ""
    print_warning "Remember to:"
    echo "   1. Update .env with your actual values"
    echo "   2. Change default passwords"
    echo "   3. Configure your domain DNS to point to this server"
}

# Main execution
main() {
    print_status "Starting deployment for $DOMAIN"
    
    check_oracle_cloud
    update_system
    install_docker
    setup_firewall
    setup_repository
    setup_environment
    setup_ssl
    deploy_application
    setup_ssl_renewal
    display_info
}

# Run main function
main "$@"