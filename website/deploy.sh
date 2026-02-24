#!/bin/bash
# Seraphonix Deployment Script - 2 Stage Deploy

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "  SERAPHONIX DEPLOYMENT"
echo "=========================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env from template...${NC}"
    cp .env.example .env 2>/dev/null || echo "JWT_SECRET=your-secret-here" > .env
    echo -e "${YELLOW}Please edit .env with your values${NC}"
fi

# ============================================
# STAGE 1: Seraphonix Gateway
# ============================================
echo ""
echo -e "${GREEN}=========================================="
echo "  STAGE 1: Seraphonix Gateway"
echo "==========================================${NC}"

echo "Building Stage 1..."
docker-compose -f docker-compose.stage1.yml build

echo "Starting Stage 1..."
docker-compose -f docker-compose.stage1.yml up -d

echo "Waiting for API..."
sleep 5

# Check health
echo "Checking health..."
curl -sf http://localhost/api/health && echo -e "${GREEN}API OK${NC}" || echo -e "${RED}API FAILED${NC}"

echo ""
echo -e "${GREEN}Stage 1 Complete!${NC}"
echo "Access: https://verilysovereign.org"
echo ""

# ============================================
# STAGE 2: Atlantiplex Studio (Optional)
# ============================================
echo -e "${YELLOW}Do you want to deploy Stage 2 (Atlantiplex Studio)?${NC}"
echo -e "${YELLOW}This will add the streaming platform at /atlantiplex/${NC}"
read -p "Deploy Stage 2? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "  STAGE 2: Atlantiplex Studio"
    echo "==========================================${NC}"
    
    # Create network if not exists
    docker network create seraphonix-network 2>/dev/null || true
    
    echo "Building Stage 2..."
    docker-compose -f docker-compose.stage2.yml build
    
    echo "Starting Stage 2..."
    docker-compose -f docker-compose.stage2.yml up -d
    
    echo ""
    echo -e "${GREEN}Stage 2 Complete!${NC}"
    echo "Access: https://verilysovereign.org/atlantiplex/"
else
    echo ""
    echo -e "${YELLOW}Stage 2 skipped.${NC}"
    echo "To deploy later: docker-compose -f docker-compose.stage2.yml up -d"
fi

echo ""
echo "=========================================="
echo "  DEPLOYMENT COMPLETE"
echo "=========================================="
echo ""
echo "Services running:"
docker-compose -f docker-compose.stage1.yml ps
docker ps --filter "name=atlantiplex" 2>/dev/null || true
