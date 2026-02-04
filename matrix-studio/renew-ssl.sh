#!/bin/bash

# SSL Certificate Renewal Script for Matrix Studio
# Runs automatically via cron job

set -e

# Configuration
DOMAIN="verilysovereign.org"
APP_DIR="/path/to/matrix-studio"  # Update this path

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Change to application directory
cd "$APP_DIR" || {
    print_error "Cannot change to directory: $APP_DIR"
    exit 1
}

print_status "Starting SSL certificate renewal for $DOMAIN"

# Check if certificates need renewal
print_status "Checking certificate expiration..."

if docker-compose run --rm certbot certificates | grep -q "Expiry Date"; then
    print_status "Renewing SSL certificates..."
    
    # Renew certificates
    docker-compose run --rm certbot renew --quiet
    
    # Reload nginx
    if docker-compose exec nginx nginx -s reload; then
        print_status "✅ SSL certificates renewed successfully"
        print_status "🔄 Nginx reloaded"
    else
        print_error "❌ Failed to reload nginx"
        exit 1
    fi
else
    print_status "SSL certificates are still valid"
fi

print_status "SSL renewal process completed"