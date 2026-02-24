.PHONY: help dev prod build stop down logs shell clean test env

help:
	@echo "Atlantiplex Studio - Docker Commands"
	@echo "====================================="
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start development environment with hot reload"
	@echo "  make dev-logs     - View development logs"
	@echo "  make dev-stop     - Stop development environment"
	@echo ""
	@echo "Production:"
	@echo "  make prod         - Start production environment"
	@echo "  make prod-logs    - View production logs"
	@echo "  make prod-stop    - Stop production environment"
	@echo ""
	@echo "Build & Maintenance:"
	@echo "  make build        - Build all images"
	@echo "  make build-nc     - Build without cache"
	@echo "  make push         - Push images to registry (requires setup)"
	@echo ""
	@echo "Utilities:"
	@echo "  make status       - Show service status"
	@echo "  make shell-stage  - Shell into Stage Server"
	@echo "  make shell-flask  - Shell into Flask Backend"
	@echo "  make shell-db     - Shell into PostgreSQL"
	@echo "  make stats        - Show resource usage"
	@echo "  make clean        - Remove all containers and volumes"
	@echo "  make test         - Run security scan on images"
	@echo "  make env          - Create .env from .env.example"
	@echo ""

# Development commands
dev:
	docker compose -f docker-compose.dev.yml up -d
	@echo "✓ Development environment started"
	@echo "  Frontend: http://localhost:5173"
	@echo "  Stage API: http://localhost:9001"
	@echo "  Flask API: http://localhost:5000"
	@echo "  PostgreSQL: localhost:5432"
	@echo "  Redis: localhost:6379"

dev-logs:
	docker compose -f docker-compose.dev.yml logs -f

dev-stop:
	docker compose -f docker-compose.dev.yml down

dev-shell-stage:
	docker compose -f docker-compose.dev.yml exec stage-server sh

dev-shell-flask:
	docker compose -f docker-compose.dev.yml exec flask-backend bash

# Production commands
prod:
	@if [ ! -f ".env.production" ]; then echo "Error: .env.production not found"; exit 1; fi
	docker compose -f docker-compose.prod.yml --env-file .env.production up -d
	@echo "✓ Production environment started"
	@echo "  Application: http://localhost"

prod-logs:
	docker compose -f docker-compose.prod.yml logs -f

prod-stop:
	docker compose -f docker-compose.prod.yml down

prod-shell-stage:
	docker compose -f docker-compose.prod.yml exec stage-server sh

prod-shell-flask:
	docker compose -f docker-compose.prod.yml exec flask-backend bash

# Build commands
build:
	docker compose build

build-nc:
	docker compose build --no-cache

build-stage:
	docker compose build stage-server

build-frontend:
	docker compose build frontend

build-flask:
	docker compose build flask-backend

# General commands
status:
	docker compose ps

stats:
	docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

logs:
	docker compose logs -f

logs-tail:
	docker compose logs --tail=100

# Database commands
db-migrate:
	docker compose exec flask-backend flask db upgrade

db-shell:
	docker compose exec postgres psql -U atlantiplex -d atlantiplex

db-backup:
	docker compose exec postgres pg_dump -U atlantiplex -d atlantiplex > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✓ Database backed up"

# Utility commands
shell-stage:
	docker compose exec stage-server sh

shell-flask:
	docker compose exec flask-backend bash

shell-db:
	docker compose exec postgres psql -U atlantiplex -d atlantiplex

shell-redis:
	docker compose exec redis redis-cli

env:
	@if [ ! -f ".env" ]; then \
		cp .env.example .env; \
		echo "✓ Created .env from .env.example"; \
		echo "⚠ Remember to edit .env with your actual values"; \
	else \
		echo ".env already exists"; \
	fi

clean:
	docker compose down -v
	docker system prune -af
	@echo "✓ Cleaned up all containers and volumes"

clean-images:
	docker image prune -af
	@echo "✓ Removed unused images"

test:
	@echo "Running security scan..."
	docker scout cves atlantiplex-stage:latest
	docker scout cves atlantiplex-frontend:latest
	docker scout cves atlantiplex-flask:latest

test-build:
	docker compose build --progress=plain

# Push to registry
push:
	@echo "Pushing images to registry..."
	docker tag atlantiplex-stage:latest ${REGISTRY}/atlantiplex-stage:latest
	docker tag atlantiplex-frontend:latest ${REGISTRY}/atlantiplex-frontend:latest
	docker tag atlantiplex-flask:latest ${REGISTRY}/atlantiplex-flask:latest
	docker push ${REGISTRY}/atlantiplex-stage:latest
	docker push ${REGISTRY}/atlantiplex-frontend:latest
	docker push ${REGISTRY}/atlantiplex-flask:latest
	@echo "✓ Images pushed to ${REGISTRY}"

# Health checks
health:
	@echo "Stage Server:" && docker compose exec stage-server wget --quiet --tries=1 --spider http://localhost:9001/health && echo "✓ Healthy" || echo "✗ Unhealthy"
	@echo "Flask Backend:" && docker compose exec flask-backend curl -f http://localhost:5000/api/health && echo "✓ Healthy" || echo "✗ Unhealthy"
	@echo "PostgreSQL:" && docker compose exec postgres pg_isready -U atlantiplex && echo "✓ Healthy" || echo "✗ Unhealthy"
	@echo "Redis:" && docker compose exec redis redis-cli ping && echo "✓ Healthy" || echo "✗ Unhealthy"

# Size information
sizes:
	@echo "Image Sizes:"
	@docker images | grep atlantiplex
	@echo ""
	@echo "Volume Sizes:"
	@docker volume ls | grep atlantiplex

# Development convenience
dev-watch:
	watch -n 1 'docker compose ps'

dev-full:
	make clean
	make env
	make dev
	@echo "✓ Full development setup complete"

# Documentation
docs:
	@echo "Documentation files:"
	@echo "  - CONTAINERIZATION_SUMMARY.md: Overview of containerization"
	@echo "  - CONTAINERIZATION_GUIDE.md: Detailed guide (12,000+ words)"
	@echo "  - DOCKER_QUICK_REFERENCE.md: Quick commands reference"
	@echo ""

.DEFAULT_GOAL := help
