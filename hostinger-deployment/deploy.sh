#!/bin/bash
# Hostinger Deployment - Quick Start Script
# Usage: bash deploy.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Atlantiplex Hostinger Deployment${NC}"
echo -e "${BLUE}================================${NC}\n"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker not found${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose found${NC}\n"

# Check .env file
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo -e "${YELLOW}Creating .env from template...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}Please edit .env with your configuration and run again${NC}"
        exit 1
    else
        echo -e "${RED}Error: .env or .env.example not found${NC}"
        exit 1
    fi
fi

# Load environment
export $(cat .env | grep -v '^#' | xargs)

echo -e "${BLUE}Configuration loaded${NC}"
echo -e "  Database: ${DB_USER}@localhost"
echo -e "  Website: ${WEBSITE_URL}"
echo -e "  Studio: ${STUDIO_URL}"
echo -e "  API: ${API_URL}\n"

# Confirm deployment
read -p "Continue with deployment? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

# Pull latest images
echo -e "${YELLOW}Pulling latest Docker images...${NC}"
docker-compose pull

# Build images
echo -e "${YELLOW}Building Docker images...${NC}"
docker-compose build --no-cache

# Stop existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose down --remove-orphans 2>/dev/null || true

# Create volumes
echo -e "${YELLOW}Creating volumes...${NC}"
docker volume create atlantiplex-postgres-data 2>/dev/null || true
docker volume create atlantiplex-redis-data 2>/dev/null || true

# Start services
echo -e "${YELLOW}Starting services...${NC}"
docker-compose up -d

# Wait for services
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Check status
echo -e "\n${BLUE}Checking service status...${NC}"
docker-compose ps

# Verify health
echo -e "\n${YELLOW}Verifying health checks...${NC}"

for i in {1..30}; do
    if curl -sf http://localhost/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Application is healthy${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

echo -e "\n${GREEN}✓ Deployment complete!${NC}\n"

echo -e "${BLUE}URLs:${NC}"
echo -e "  Website: ${WEBSITE_URL}"
echo -e "  Studio: ${STUDIO_URL}"
echo -e "  API: ${API_URL}"

echo -e "\n${BLUE}Useful Commands:${NC}"
echo -e "  View logs: ${GREEN}docker-compose logs -f${NC}"
echo -e "  Stop services: ${GREEN}docker-compose down${NC}"
echo -e "  Restart services: ${GREEN}docker-compose restart${NC}"
echo -e "  Enter database: ${GREEN}docker-compose exec postgres psql -U ${DB_USER}${NC}"
echo -e "  View Redis: ${GREEN}docker-compose exec redis redis-cli${NC}\n"

echo -e "${YELLOW}Important:${NC}"
echo -e "  1. Update your DNS records to point to this server"
echo -e "  2. Generate SSL certificates (Let's Encrypt recommended)"
echo -e "  3. Update nginx/conf.d config with your domain names"
echo -e "  4. Restart nginx after SSL setup: docker-compose restart nginx\n"
