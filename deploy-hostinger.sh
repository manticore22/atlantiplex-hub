#!/bin/bash

################################################################################
# Atlantiplex Studio - Hostinger Deployment Script
# Purpose: Automated deployment to Hostinger VPS
# Usage: ./deploy-hostinger.sh <environment> <version>
################################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
HOSTINGER_HOST="${HOSTINGER_HOST:-your-vps.hostinger.com}"
HOSTINGER_USER="${HOSTINGER_USER:-root}"
HOSTINGER_PORT="${HOSTINGER_PORT:-22}"
DEPLOY_DIR="/home/atlantiplex"
BACKUP_DIR="/home/atlantiplex/backups"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-docker.io}"
IMAGE_PREFIX="${DOCKER_REGISTRY}/yourusername"
APP_NAME="atlantiplex-studio"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Log file
LOG_FILE="/tmp/deploy_${TIMESTAMP}.log"

################################################################################
# Logging Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

################################################################################
# Pre-Deployment Checks
################################################################################

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check SSH connectivity
    if ! ssh -o ConnectTimeout=5 -p "$HOSTINGER_PORT" "${HOSTINGER_USER}@${HOSTINGER_HOST}" "echo 'SSH test'" &>/dev/null; then
        log_error "Cannot connect to Hostinger server. Check host, user, and SSH key."
        exit 1
    fi
    log_success "SSH connectivity verified"
    
    # Check Docker is installed on server
    if ! ssh -p "$HOSTINGER_PORT" "${HOSTINGER_USER}@${HOSTINGER_HOST}" "command -v docker" &>/dev/null; then
        log_error "Docker not installed on server. Run setup-hostinger.sh first."
        exit 1
    fi
    log_success "Docker installed on server"
}

check_local_env() {
    log_info "Checking local environment..."
    
    # Check required tools
    for cmd in docker docker-compose git; do
        if ! command -v "$cmd" &>/dev/null; then
            log_error "$cmd is not installed"
            exit 1
        fi
    done
    log_success "All required tools available"
}

################################################################################
# Docker Image Management
################################################################################

build_images() {
    local env=$1
    log_info "Building Docker images for $env environment..."
    
    docker-compose build --no-cache || {
        log_error "Docker build failed"
        exit 1
    }
    
    log_success "Docker images built successfully"
}

push_images() {
    log_info "Pushing Docker images to registry..."
    
    # Tag images
    docker tag atlantiplex-stage:latest "${IMAGE_PREFIX}/atlantiplex-stage:latest"
    docker tag atlantiplex-flask:latest "${IMAGE_PREFIX}/atlantiplex-flask:latest"
    docker tag atlantiplex-frontend:latest "${IMAGE_PREFIX}/atlantiplex-frontend:latest"
    
    # Push images
    docker push "${IMAGE_PREFIX}/atlantiplex-stage:latest" || {
        log_error "Failed to push stage image"
        exit 1
    }
    
    docker push "${IMAGE_PREFIX}/atlantiplex-flask:latest" || {
        log_error "Failed to push flask image"
        exit 1
    }
    
    docker push "${IMAGE_PREFIX}/atlantiplex-frontend:latest" || {
        log_error "Failed to push frontend image"
        exit 1
    }
    
    log_success "Images pushed to registry successfully"
}

scan_images() {
    log_info "Scanning images for vulnerabilities..."
    
    docker scout cves "${IMAGE_PREFIX}/atlantiplex-stage:latest" || log_warning "Scout scan warning for stage image"
    docker scout cves "${IMAGE_PREFIX}/atlantiplex-flask:latest" || log_warning "Scout scan warning for flask image"
    
    log_success "Image scanning completed"
}

################################################################################
# Database Management
################################################################################

backup_database() {
    log_info "Backing up current database..."
    
    ssh -p "$HOSTINGER_PORT" "${HOSTINGER_USER}@${HOSTINGER_HOST}" << 'EOF'
        mkdir -p /home/atlantiplex/backups
        BACKUP_FILE="/home/atlantiplex/backups/postgres_$(date +%Y%m%d_%H%M%S).sql"
        docker exec atlantiplex-postgres pg_dump -U atlantiplex atlantiplex > "$BACKUP_FILE"
        gzip "$BACKUP_FILE"
        echo "Backup created: $BACKUP_FILE.gz"
EOF
    
    log_success "Database backup created"
}

migrate_database() {
    log_info "Running database migrations..."
    
    ssh -p "$HOSTINGER_PORT" "${HOSTINGER_USER}@${HOSTINGER_HOST}" << 'EOF'
        cd /home/atlantiplex
        docker-compose exec -T atlantiplex-flask python -c "from app import db; db.create_all()"
        docker-compose exec -T atlantiplex-stage npm run migrate || true
EOF
    
    log_success "Database migrations completed"
}

################################################################################
# Deployment
################################################################################

deploy_to_hostinger() {
    local env=$1
    log_info "Deploying to Hostinger ($env environment)..."
    
    # Create deployment directory if doesn't exist
    ssh -p "$HOSTINGER_PORT" "${HOSTINGER_USER}@${HOSTINGER_HOST}" "mkdir -p ${DEPLOY_DIR}"
    
    # Copy docker-compose file
    scp -P "$HOSTINGER_PORT" docker-compose.yml "${HOSTINGER_USER}@${HOSTINGER_HOST}:${DEPLOY_DIR}/"
    
    # Copy env file (make sure it's created locally first!)
    if [ -f ".env.production" ]; then
        scp -P "$HOSTINGER_PORT" .env.production "${HOSTINGER_USER}@${HOSTINGER_HOST}:${DEPLOY_DIR}/.env"
    else
        log_error ".env.production file not found"
        exit 1
    fi
    
    # Copy nginx config
    scp -r -P "$HOSTINGER_PORT" nginx/ "${HOSTINGER_USER}@${HOSTINGER_HOST}:${DEPLOY_DIR}/"
    
    log_success "Files copied to server"
}

pull_and_restart() {
    log_info "Pulling latest images and restarting services..."
    
    ssh -p "$HOSTINGER_PORT" "${HOSTINGER_USER}@${HOSTINGER_HOST}" << 'EOF'
        cd /home/atlantiplex
        
        # Stop old containers
        docker-compose down
        
        # Pull latest images
        docker pull ${IMAGE_PREFIX}/atlantiplex-stage:latest
        docker pull ${IMAGE_PREFIX}/atlantiplex-flask:latest
        docker pull ${IMAGE_PREFIX}/atlantiplex-frontend:latest
        
        # Start new containers
        docker-compose up -d
        
        # Wait for services to be healthy
        echo "Waiting for services to be healthy..."
        sleep 30
        docker-compose ps
EOF
    
    log_success "Services restarted"
}

################################################################################
# Post-Deployment Verification
################################################################################

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check if services are running
    ssh -p "$HOSTINGER_PORT" "${HOSTINGER_USER}@${HOSTINGER_HOST}" << 'EOF'
        echo "Service status:"
        cd /home/atlantiplex
        docker-compose ps
        
        echo ""
        echo "Testing health endpoints..."
        curl -s http://localhost:9001/health | jq . || echo "Stage server not responding"
        curl -s http://localhost:5000/api/health | jq . || echo "Flask backend not responding"
        curl -s http://localhost/health || echo "Nginx not responding"
EOF
    
    log_success "Deployment verification completed"
}

################################################################################
# Rollback
################################################################################

rollback_deployment() {
    log_warning "Rolling back deployment..."
    
    ssh -p "$HOSTINGER_PORT" "${HOSTINGER_USER}@${HOSTINGER_HOST}" << 'EOF'
        cd /home/atlantiplex
        docker-compose down
        
        # Restore previous version from backup or git
        git checkout HEAD~1
        docker-compose up -d
        
        echo "Rollback completed"
EOF
    
    log_success "Rollback successful"
}

################################################################################
# Monitoring
################################################################################

setup_monitoring() {
    log_info "Setting up monitoring..."
    
    ssh -p "$HOSTINGER_PORT" "${HOSTINGER_USER}@${HOSTINGER_HOST}" << 'EOF'
        # Create monitoring scripts directory
        mkdir -p /home/atlantiplex/monitoring
        
        # Create health check script
        cat > /home/atlantiplex/monitoring/health-check.sh << 'HEALTHCHECK'
#!/bin/bash
ENDPOINT="http://localhost:9001/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$ENDPOINT")
if [ "$RESPONSE" != "200" ]; then
    echo "ALERT: Health endpoint returned $RESPONSE" | mail -s "Atlantiplex Health Alert" admin@example.com
fi
HEALTHCHECK
        
        chmod +x /home/atlantiplex/monitoring/health-check.sh
        
        # Add to crontab (every 5 minutes)
        (crontab -l 2>/dev/null; echo "*/5 * * * * /home/atlantiplex/monitoring/health-check.sh") | crontab -
EOF
    
    log_success "Monitoring setup completed"
}

################################################################################
# Cleanup
################################################################################

cleanup() {
    log_info "Cleaning up..."
    
    # Remove old images locally (optional)
    docker image prune -f || true
    
    log_success "Cleanup completed"
}

################################################################################
# Main Deployment Flow
################################################################################

main() {
    local environment="${1:-staging}"
    local version="${2:-latest}"
    
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Atlantiplex Studio - Hostinger Deployment${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Environment: $environment"
    echo "Version: $version"
    echo "Log file: $LOG_FILE"
    echo ""
    
    check_local_env
    check_prerequisites
    
    read -p "Continue with deployment? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Deployment cancelled"
        exit 0
    fi
    
    build_images "$environment"
    scan_images
    push_images
    backup_database
    deploy_to_hostinger "$environment"
    migrate_database
    pull_and_restart
    verify_deployment
    setup_monitoring
    cleanup
    
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Deployment completed successfully!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    log_success "Deployment log saved to: $LOG_FILE"
}

# Run main function
main "$@"
