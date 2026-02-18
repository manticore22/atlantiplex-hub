#!/bin/bash
#
# Atlantiplex Studio - Management Script
# Use this to manage your bare metal deployment
#

INSTALL_DIR="/opt/atlantiplex"
COMPOSE_FILE="$INSTALL_DIR/docker-compose.yml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Check if running from install directory
check_directory() {
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Cannot find docker-compose.yml in $INSTALL_DIR"
        log_info "Are you in the right directory?"
        exit 1
    fi
}

# Start services
start() {
    log_info "Starting Atlantiplex Studio..."
    cd $INSTALL_DIR
    docker-compose up -d
    log_success "Services started"
    status
}

# Stop services
stop() {
    log_info "Stopping Atlantiplex Studio..."
    cd $INSTALL_DIR
    docker-compose down
    log_success "Services stopped"
}

# Restart services
restart() {
    log_info "Restarting Atlantiplex Studio..."
    cd $INSTALL_DIR
    docker-compose restart
    log_success "Services restarted"
    status
}

# View status
status() {
    log_info "Service Status:"
    cd $INSTALL_DIR
    docker-compose ps
    
    echo ""
    log_info "Health Checks:"
    
    if curl -f http://localhost:9001/health > /dev/null 2>&1; then
        log_success "Stage Server (Node.js): RUNNING"
    else
        log_error "Stage Server (Node.js): DOWN"
    fi
    
    if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
        log_success "Flask Backend (Python): RUNNING"
    else
        log_error "Flask Backend (Python): DOWN"
    fi
    
    if pgrep -x "nginx" > /dev/null; then
        log_success "Nginx: RUNNING"
    else
        log_error "Nginx: DOWN"
    fi
    
    if systemctl is-active --quiet postgresql; then
        log_success "PostgreSQL: RUNNING"
    else
        log_error "PostgreSQL: DOWN"
    fi
    
    if systemctl is-active --quiet redis-server; then
        log_success "Redis: RUNNING"
    else
        log_error "Redis: DOWN"
    fi
}

# View logs
logs() {
    cd $INSTALL_DIR
    
    if [ -z "$1" ]; then
        log_info "Showing all logs (Ctrl+C to exit)..."
        docker-compose logs -f
    else
        log_info "Showing logs for $1..."
        docker-compose logs -f $1
    fi
}

# Update application
update() {
    log_info "Updating Atlantiplex Studio..."
    cd $INSTALL_DIR
    
    log_info "Pulling latest changes..."
    git pull
    
    log_info "Rebuilding containers..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    
    log_success "Update complete"
    status
}

# Backup data
backup() {
    BACKUP_DIR="/opt/backups/atlantiplex"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
    
    log_info "Creating backup..."
    mkdir -p $BACKUP_DIR
    
    # Backup database
    docker-compose exec -T postgres pg_dump -U atlantiplex atlantiplex > $BACKUP_DIR/db_$TIMESTAMP.sql
    
    # Backup uploads and recordings
    tar -czf $BACKUP_FILE \
        $INSTALL_DIR/data \
        $BACKUP_DIR/db_$TIMESTAMP.sql \
        $INSTALL_DIR/.env
    
    # Remove SQL file (included in tar)
    rm $BACKUP_DIR/db_$TIMESTAMP.sql
    
    log_success "Backup created: $BACKUP_FILE"
    
    # Clean old backups (keep last 7 days)
    find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete
}

# Restore from backup
restore() {
    if [ -z "$1" ]; then
        log_error "Please specify backup file"
        log_info "Usage: $0 restore <backup_file>"
        exit 1
    fi
    
    BACKUP_FILE="$1"
    
    if [ ! -f "$BACKUP_FILE" ]; then
        log_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    log_warning "This will overwrite current data! Are you sure? (yes/no)"
    read confirm
    
    if [ "$confirm" != "yes" ]; then
        log_info "Restore cancelled"
        exit 0
    fi
    
    log_info "Restoring from backup..."
    
    # Stop services
    cd $INSTALL_DIR
    docker-compose down
    
    # Extract backup
    tar -xzf $BACKUP_FILE -C /
    
    # Restore database
    if [ -f "/tmp/db_restore.sql" ]; then
        docker-compose up -d postgres
        sleep 5
        docker-compose exec -T postgres psql -U atlantiplex -d atlantiplex < /tmp/db_restore.sql
        rm /tmp/db_restore.sql
    fi
    
    # Start services
    docker-compose up -d
    
    log_success "Restore complete"
}

# Show system stats
stats() {
    log_info "System Resources:"
    echo "CPU Usage:"
    top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk '{print "  " $1 "%"}'
    
    echo ""
    echo "Memory Usage:"
    free -h | grep "Mem:" | awk '{print "  Used: " $3 " / " $2}'
    
    echo ""
    echo "Disk Usage:"
    df -h / | tail -1 | awk '{print "  Used: " $3 " / " $2 " (" $5 ")"}'
    
    echo ""
    log_info "Docker Stats:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# SSL certificate management
ssl() {
    case $1 in
        renew)
            log_info "Renewing SSL certificates..."
            certbot renew --quiet
            systemctl reload nginx
            log_success "SSL certificates renewed"
            ;;
        status)
            log_info "SSL Certificate Status:"
            certbot certificates
            ;;
        *)
            log_error "Unknown SSL command: $1"
            log_info "Usage: $0 ssl [renew|status]"
            ;;
    esac
}

# Show help
help() {
    cat << EOF
Atlantiplex Studio - Management Script

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    start              Start all services
    stop               Stop all services
    restart            Restart all services
    status             Show service status
    logs [service]     View logs (optionally specify service)
    update             Update to latest version
    backup             Create backup of data
    restore <file>     Restore from backup file
    stats              Show system statistics
    ssl renew          Renew SSL certificates
    ssl status         Show SSL certificate status
    help               Show this help message

Services for logs:
    nginx, stage-server, flask-backend, postgres, redis

Examples:
    $0 start                    # Start all services
    $0 logs                    # View all logs
    $0 logs stage-server       # View only stage server logs
    $0 backup                  # Create backup
    $0 restore /opt/backups/atlantiplex/backup_20240115_120000.tar.gz

EOF
}

# Main
case $1 in
    start)
        check_directory
        start
        ;;
    stop)
        check_directory
        stop
        ;;
    restart)
        check_directory
        restart
        ;;
    status)
        check_directory
        status
        ;;
    logs)
        check_directory
        logs $2
        ;;
    update)
        check_directory
        update
        ;;
    backup)
        check_directory
        backup
        ;;
    restore)
        check_directory
        restore $2
        ;;
    stats)
        stats
        ;;
    ssl)
        ssl $2
        ;;
    help|--help|-h)
        help
        ;;
    *)
        log_error "Unknown command: $1"
        help
        exit 1
        ;;
esac
