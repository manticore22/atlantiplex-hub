#!/bin/bash
# Atlantiplex Kubernetes Deployment Script
# Usage: ./deploy-k8s.sh [environment] [registry]

set -e

ENVIRONMENT=${1:-staging}
REGISTRY=${2:-docker.io/atlantiplex}
IMAGE_TAG=${3:-latest}

echo "=========================================="
echo "Atlantiplex Kubernetes Deployment"
echo "=========================================="
echo "Environment: $ENVIRONMENT"
echo "Registry: $REGISTRY"
echo "Image Tag: $IMAGE_TAG"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Check prerequisites
log_info "Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    log_error "kubectl not found. Please install kubectl."
    exit 1
fi

if ! command -v docker &> /dev/null; then
    log_warn "docker not found. Skipping image build."
else
    log_info "docker found."
fi

CLUSTER_NAME=$(kubectl config current-context)
log_info "Connected to cluster: $CLUSTER_NAME"

# Step 2: Create namespace
log_info "Creating namespace..."
kubectl create namespace atlantiplex --dry-run=client -o yaml | kubectl apply -f -

# Step 3: Apply configuration
log_info "Applying ConfigMaps..."
kubectl apply -f k8s/01-namespace-configmap.yaml

# Step 4: Verify secrets exist (don't overwrite if already present)
log_info "Checking secrets..."
if kubectl get secret atlantiplex-secrets -n atlantiplex &> /dev/null; then
    log_warn "Secrets already exist. Skipping secret creation."
    log_warn "To update secrets, delete and recreate: kubectl delete secret atlantiplex-secrets -n atlantiplex"
else
    log_error "Secrets not found. Please create them first:"
    echo "  kubectl create secret generic atlantiplex-secrets \\"
    echo "    --from-literal=DB_PASSWORD='...'"
    echo "    -n atlantiplex"
    exit 1
fi

# Step 5: Deploy databases
log_info "Deploying PostgreSQL..."
kubectl apply -f k8s/03-postgres.yaml

log_info "Deploying Redis..."
kubectl apply -f k8s/04-redis.yaml

# Step 6: Wait for databases
log_info "Waiting for databases to be ready (up to 5 minutes)..."
kubectl wait --for=condition=Ready pod -l app=postgres -n atlantiplex --timeout=300s 2>/dev/null || {
    log_warn "PostgreSQL not ready yet. Continuing anyway..."
}

kubectl wait --for=condition=Ready pod -l app=redis -n atlantiplex --timeout=300s 2>/dev/null || {
    log_warn "Redis not ready yet. Continuing anyway..."
}

# Step 7: Deploy application services
log_info "Deploying Node.js services..."
kubectl apply -f k8s/05-node-deployments.yaml

log_info "Deploying Flask backend..."
kubectl apply -f k8s/06-flask-deployment.yaml

log_info "Deploying frontend and ingress..."
kubectl apply -f k8s/07-frontend-ingress.yaml

# Step 8: Summary
log_info "Deployment initiated!"
echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Monitor deployment status:"
echo "   kubectl get pods -n atlantiplex -w"
echo ""
echo "2. Check service status:"
echo "   kubectl get svc -n atlantiplex"
echo ""
echo "3. Get external IP (wait for LoadBalancer):"
echo "   kubectl get svc nginx-ingress -n atlantiplex"
echo ""
echo "4. View logs:"
echo "   kubectl logs -f deployment/stage-server -n atlantiplex"
echo ""
echo "5. Configure DNS with external IP"
echo ""
echo "=========================================="
echo ""

# Print deployment status
log_info "Deployment status:"
kubectl get all -n atlantiplex --no-headers
