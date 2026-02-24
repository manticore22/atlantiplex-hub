#!/bin/bash

################################################################################
# Atlantiplex Studio - Interactive Launch Wizard
# Purpose: Guide user through setup with validation
# Usage: ./launch-wizard.sh
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# State file
STATE_FILE=".launch-state"

################################################################################
# Utility Functions
################################################################################

clear_screen() {
    clear
}

header() {
    clear_screen
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  Atlantiplex Studio - Launch Wizard${NC}                    ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

section_title() {
    echo -e "${BLUE}▶ $1${NC}"
    echo ""
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

error() {
    echo -e "${RED}✗ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

prompt_yes_no() {
    local question=$1
    local response
    read -p "$(echo -e ${BLUE}$question' (y/n): '${NC})" response
    [[ "$response" =~ ^[Yy]$ ]]
}

prompt_input() {
    local question=$1
    local default=${2:-}
    local response
    
    if [ -z "$default" ]; then
        read -p "$(echo -e ${BLUE}$question': '${NC})" response
    else
        read -p "$(echo -e ${BLUE}$question' ['$default']: '${NC})" response
        response=${response:-$default}
    fi
    echo "$response"
}

prompt_password() {
    local question=$1
    local response
    read -sp "$(echo -e ${BLUE}$question': '${NC})" response
    echo "$response"
}

################################################################################
# Validation Functions
################################################################################

validate_url() {
    local url=$1
    [[ $url =~ ^https?:// ]]
}

validate_password() {
    local pass=$1
    if [ ${#pass} -lt 32 ]; then
        error "Password too short (min 32 chars). Generated: $(openssl rand -hex 16)"
        return 1
    fi
    return 0
}

validate_email() {
    local email=$1
    [[ $email =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]
}

validate_ip() {
    local ip=$1
    [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]
}

################################################################################
# Step Functions
################################################################################

step_welcome() {
    header
    section_title "Welcome to Atlantiplex Launch Wizard"
    
    echo "This wizard will guide you through:"
    echo "  1. Pre-flight checks"
    echo "  2. Environment configuration"
    echo "  3. VPS setup"
    echo "  4. Application deployment"
    echo "  5. Validation & monitoring"
    echo ""
    
    info "Total time: ~30 minutes"
    
    if ! prompt_yes_no "Ready to launch?"; then
        echo "Cancelled."
        exit 0
    fi
    
    success "Starting setup..."
    sleep 1
}

step_preflight() {
    header
    section_title "Step 1: Pre-Flight Checks"
    
    echo "Checking local environment..."
    echo ""
    
    # Check Docker
    if command -v docker &>/dev/null; then
        success "Docker installed ($(docker --version | grep -oP 'Docker version \K[^,]+'))"
    else
        error "Docker not installed"
        error "Visit: https://docs.docker.com/get-docker/"
        return 1
    fi
    
    # Check Docker Compose
    if command -v docker-compose &>/dev/null; then
        success "Docker Compose installed"
    else
        error "Docker Compose not installed"
        return 1
    fi
    
    # Check Git
    if command -v git &>/dev/null; then
        success "Git installed"
    else
        error "Git not installed"
        return 1
    fi
    
    # Check SSH
    if command -v ssh &>/dev/null; then
        success "SSH installed"
    else
        error "SSH not installed"
        return 1
    fi
    
    echo ""
    info "All local tools ready!"
    
    read -p "Press enter to continue..."
    return 0
}

step_hostinger() {
    header
    section_title "Step 2: Hostinger VPS Setup"
    
    echo "You need a Hostinger VPS:"
    echo "  • Recommended: Business VPS (8GB RAM, 160GB SSD)"
    echo "  • Minimum: Standard VPS (4GB RAM, 60GB SSD)"
    echo ""
    
    if prompt_yes_no "Do you have a Hostinger VPS provisioned?"; then
        local ip=$(prompt_input "Enter VPS IP address")
        if ! validate_ip "$ip"; then
            error "Invalid IP address"
            return 1
        fi
        
        local user=$(prompt_input "Enter SSH user (default: root)" "root")
        local port=$(prompt_input "Enter SSH port (default: 22)" "22")
        
        # Test SSH
        info "Testing SSH connection..."
        if ssh -o ConnectTimeout=5 -p "$port" "$user@$ip" "echo OK" &>/dev/null; then
            success "SSH connection successful"
            
            # Save config
            echo "HOSTINGER_IP=$ip" >> "$STATE_FILE"
            echo "HOSTINGER_USER=$user" >> "$STATE_FILE"
            echo "HOSTINGER_PORT=$port" >> "$STATE_FILE"
            
            return 0
        else
            error "Cannot connect to VPS"
            error "Check IP, user, port, and firewall settings"
            return 1
        fi
    else
        info "Visit: https://www.hostinger.com/business-hosting"
        info "Come back after provisioning"
        return 1
    fi
}

step_domain() {
    header
    section_title "Step 3: Domain Configuration"
    
    local domain=$(prompt_input "Enter your domain (e.g., example.com)")
    
    if validate_url "https://$domain"; then
        success "Domain noted: $domain"
        echo "DOMAIN=$domain" >> "$STATE_FILE"
        
        warning "Next: Point DNS records to your VPS IP"
        echo "  A Record: $domain → YOUR_VPS_IP"
        echo "  A Record: www.$domain → YOUR_VPS_IP"
        echo ""
        info "Wait 24-48 hours for DNS propagation"
        
        read -p "Press enter to continue..."
        return 0
    else
        error "Invalid domain"
        return 1
    fi
}

step_secrets() {
    header
    section_title "Step 4: Generate Secrets"
    
    echo "You need to generate secure secrets:"
    echo ""
    
    # Database password
    info "Generating database password..."
    local db_pass=$(openssl rand -hex 16)
    echo "DATABASE_PASSWORD=$db_pass" >> "$STATE_FILE"
    success "Generated: $(echo $db_pass | cut -c1-8)****"
    
    # Redis password
    info "Generating Redis password..."
    local redis_pass=$(openssl rand -hex 16)
    echo "REDIS_PASSWORD=$redis_pass" >> "$STATE_FILE"
    success "Generated: $(echo $redis_pass | cut -c1-8)****"
    
    # JWT secret
    info "Generating JWT secret..."
    local jwt_secret=$(openssl rand -hex 16)
    echo "JWT_SECRET=$jwt_secret" >> "$STATE_FILE"
    success "Generated: $(echo $jwt_secret | cut -c1-8)****"
    
    echo ""
    warning "Store these secrets securely (1Password, Vault, etc.)"
    warning "NEVER commit to Git"
    
    read -p "Press enter to continue..."
    return 0
}

step_apis() {
    header
    section_title "Step 5: API Keys & Credentials"
    
    echo "Enter your API keys (leave blank to skip for now):"
    echo ""
    
    # Stripe
    local stripe=$(prompt_input "Stripe Secret Key" "")
    if [ -n "$stripe" ]; then
        echo "STRIPE_SECRET_KEY=$stripe" >> "$STATE_FILE"
        success "Stripe key configured"
    fi
    
    # Email
    local email=$(prompt_input "SMTP Email" "")
    if [ -n "$email" ]; then
        if validate_email "$email"; then
            echo "SMTP_USER=$email" >> "$STATE_FILE"
            success "Email configured"
        else
            warning "Invalid email"
        fi
    fi
    
    # Email password
    local email_pass=$(prompt_input "SMTP Password (if needed)" "")
    if [ -n "$email_pass" ]; then
        echo "SMTP_PASSWORD=$email_pass" >> "$STATE_FILE"
    fi
    
    echo ""
    info "You can update these later in .env.production"
    
    read -p "Press enter to continue..."
    return 0
}

step_setup_vps() {
    header
    section_title "Step 6: Setup VPS"
    
    source "$STATE_FILE"
    
    echo "Running automated VPS setup..."
    echo "This will:"
    echo "  • Update system packages"
    echo "  • Install Docker"
    echo "  • Configure firewall"
    echo "  • Set up SSL"
    echo "  • Enable monitoring"
    echo ""
    
    if prompt_yes_no "Proceed with VPS setup?"; then
        info "Starting setup (this takes ~10 minutes)..."
        
        # Run setup
        if ssh -p "$HOSTINGER_PORT" "$HOSTINGER_USER@$HOSTINGER_IP" 'bash -s' < setup-hostinger.sh; then
            success "VPS setup completed!"
            echo "SETUP_VPS_DONE=1" >> "$STATE_FILE"
            return 0
        else
            error "VPS setup failed"
            return 1
        fi
    else
        warning "Run manually later: ssh $HOSTINGER_USER@$HOSTINGER_IP 'bash -s' < setup-hostinger.sh"
        return 0
    fi
}

step_deploy() {
    header
    section_title "Step 7: Deploy Application"
    
    echo "Ready to deploy?"
    echo ""
    echo "This will:"
    echo "  • Build Docker images"
    echo "  • Push to registry"
    echo "  • Deploy to production"
    echo "  • Run health checks"
    echo ""
    
    if prompt_yes_no "Deploy now?"; then
        info "Building images..."
        docker-compose build --quiet
        success "Images built"
        
        info "Deploying..."
        if ./deploy-hostinger.sh production latest; then
            success "Deployment completed!"
            echo "DEPLOYED=1" >> "$STATE_FILE"
            return 0
        else
            error "Deployment failed"
            return 1
        fi
    else
        warning "Run manually: ./deploy-hostinger.sh production latest"
        return 0
    fi
}

step_validate() {
    header
    section_title "Step 8: Validation"
    
    source "$STATE_FILE"
    
    echo "Running validation checks..."
    echo ""
    
    # Check services
    info "Checking services..."
    if ssh -p "$HOSTINGER_PORT" "$HOSTINGER_USER@$HOSTINGER_IP" \
        "cd /home/atlantiplex && docker-compose ps" 2>/dev/null | grep -q "Up"; then
        success "Services running"
    else
        error "Services not responding"
        return 1
    fi
    
    # Check health
    info "Checking health endpoints..."
    if curl -s http://$HOSTINGER_IP:9001/health &>/dev/null; then
        success "Stage server healthy"
    else
        warning "Stage server not responding (DNS may not be ready)"
    fi
    
    echo ""
    success "Validation complete!"
    
    read -p "Press enter to continue..."
    return 0
}

step_summary() {
    header
    section_title "Launch Complete! 🎉"
    
    source "$STATE_FILE"
    
    echo "Your application is running:"
    echo ""
    echo -e "  ${GREEN}Domain${NC}: https://${DOMAIN}"
    echo -e "  ${GREEN}API${NC}: https://${DOMAIN}/api"
    echo -e "  ${GREEN}Health${NC}: https://${DOMAIN}/health"
    echo ""
    
    echo "Next steps:"
    echo "  1. Wait 24-48 hours for DNS propagation"
    echo "  2. Test your domain: https://$DOMAIN"
    echo "  3. Monitor: docker-compose ps"
    echo "  4. Check logs: docker-compose logs -f"
    echo ""
    
    echo "For support:"
    echo "  • Docs: see QUICK_START.md"
    echo "  • Troubleshooting: see HOSTINGER_DEPLOYMENT_GUIDE.md"
    echo "  • Hostinger Support: https://www.hostinger.com/help"
    echo ""
    
    success "You're live!"
}

################################################################################
# Main Flow
################################################################################

main() {
    # Initialize state file
    > "$STATE_FILE"
    
    # Run steps
    step_welcome || exit 1
    step_preflight || { error "Pre-flight failed"; exit 1; }
    step_hostinger || { error "Hostinger setup failed"; exit 1; }
    step_domain || { error "Domain config failed"; exit 1; }
    step_secrets || { error "Secrets generation failed"; exit 1; }
    step_apis || true  # Optional
    step_setup_vps || { error "VPS setup failed"; exit 1; }
    step_deploy || { error "Deployment failed"; exit 1; }
    step_validate || { error "Validation failed"; exit 1; }
    step_summary
    
    # Cleanup
    rm -f "$STATE_FILE"
    
    echo "State file saved at: .launch-state"
    info "Launch wizard completed successfully!"
}

main "$@"
