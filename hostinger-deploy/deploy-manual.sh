#!/bin/bash
set -euo pipefail

REGISTRY="docker.io/manticore313/website_and_studio"
REPO_DIR="/opt/atlantiplex"

echo "Atlantiplex Hostinger Deploy (hub-only, no TLS)"
echo "Pulling hub images..."
docker login docker.io || true
docker pull "$REGISTRY:website"
docker pull "$REGISTRY:studio"
docker pull "$REGISTRY:stage"
docker pull "$REGISTRY:flask"

echo "Ensuring deployment dir..."
mkdir -p "$REPO_DIR" /opt/atlantiplex/nginx
cd "$REPO_DIR"

echo "Bringing stack down (if running)..."
docker-compose -f docker-compose.prod.yml down || true

echo "Bringing stack up..."
docker-compose -f docker-compose.prod.yml up -d

echo "Health checks..."
set +e
curl -sS http://verilysovereign.online/health || true
curl -sS http://website.verilysovereign.online/health || true
curl -sS http://studio.verilysovereign.online/health || true
echo "DONE"
