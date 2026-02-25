#!/bin/bash
set -e

REGISTRY="docker.io/manticore313/website_and_studio"
IMAGE_TAG="${IMAGE_TAG:-latest}"
VPS_HOST="76.13.242.128"
VPS_USER="root"

echo "=== Atlantiplex Deployment (No TLS) ==="
echo "Registry: $REGISTRY"
echo "VPS: $VPS_HOST"

echo ""
echo "=== Step 1: Building images locally ==="

echo "Building website..."
docker build -t $REGISTRY:website ./website

echo "Building studio..."
# Use pre-built dist folder
docker build -t $REGISTRY:studio -f - ./AtlantiplexStudio/web/frontend <<'EOF'
FROM nginx:stable-alpine
COPY dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF

echo "Building stage server..."
docker build -t $REGISTRY:stage ./matrix-studio/web/stage

echo "Building flask backend..."
docker build -t $REGISTRY:flask -f ./matrix-studio/Dockerfile.python ./matrix-studio

echo ""
echo "=== Step 2: Pushing images to Docker Hub ==="

echo "Pushing website..."
docker push $REGISTRY:website

echo "Pushing studio..."
docker push $REGISTRY:studio

echo "Pushing stage..."
docker push $REGISTRY:stage

echo "Pushing flask..."
docker push $REGISTRY:flask

echo ""
echo "=== Step 3: Setting up VPS ==="

ssh $VPS_USER@$VPS_HOST "mkdir -p /opt/atlantiplex/{nginx,nginx/sites-enabled,nginx/ssl}"

echo "Copying docker-compose.prod.yml..."
scp docker-compose.prod.yml $VPS_USER@$VPS_HOST:/opt/atlantiplex/

echo "Copying nginx config..."
scp nginx/nginx.conf $VPS_USER@$VPS_HOST:/opt/atlantiplex/nginx/

echo "Creating directories on VPS..."
ssh $VPS_USER@$VPS_HOST "mkdir -p /data/atlantiplex/{postgres,redis}"

echo ""
echo "=== Step 4: Creating .env file on VPS ==="

ssh $VPS_USER@$VPS_HOST << 'EOF'
cd /opt/atlantiplex
cat > .env << 'ENDFILE'
DB_USER=atlantiplex
DB_PASSWORD=Atlantiplex2024Secure!
DB_NAME=atlantiplex
REDIS_PASSWORD=AtlantiplexRedis2024!
JWT_SECRET=AtlantiplexJWT2024SecretKey!
JWT_REFRESH_SECRET=AtlantiplexRefresh2024Secret!
STRIPE_SECRET_KEY="${STRIPE_SECRET_KEY:-}"
STRIPE_PUBLISHABLE_KEY="${STRIPE_PUBLISHABLE_KEY:-}"
STRIPE_WEBHOOK_SECRET="${STRIPE_WEBHOOK_SECRET:-}"
CORS_ORIGIN="${CORS_ORIGIN:-http://verilysovereign.online}"
API_URL="${API_URL:-http://verilysovereign.online/api/flask}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
ENDFILE
EOF

echo ""
echo "=== Step 5: Starting the stack ==="

ssh $VPS_USER@$VPS_HOST "cd /opt/atlantiplex && docker-compose -f docker-compose.prod.yml up -d"

echo ""
echo "=== Deployment complete! ==="
echo "Website: http://verilysovereign.online"
echo "Studio: http://studio.verilysovereign.online"
echo ""
echo "Check status with: ssh $VPS_USER@$VPS_HOST 'docker-compose -f /opt/atlantiplex/docker-compose.prod.yml ps'"
