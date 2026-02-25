#!/bin/bash
# Kubernetes Deployment Script for Atlantiplex Studio

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="atlantiplex"
REGISTRY="${DOCKER_REGISTRY:-docker.io}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
DOMAIN="${DOMAIN:-atlantiplex.example.com}"
TIMEOUT="${TIMEOUT:-300}"

echo -e "${YELLOW}Atlantiplex Kubernetes Deployment Script${NC}"
echo "=========================================="

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

# Check prerequisites
log_info "Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    log_error "kubectl not found. Please install kubectl."
    exit 1
fi

if ! command -v sed &> /dev/null; then
    log_error "sed not found. Please install sed."
    exit 1
fi

# Verify cluster connection
if ! kubectl cluster-info &> /dev/null; then
    log_error "Cannot connect to Kubernetes cluster. Please configure kubectl."
    exit 1
fi

log_info "✓ kubectl is installed and cluster is accessible"

# Verify manifests directory
if [ ! -d "k8s-optimized" ]; then
    log_error "k8s-optimized directory not found. Run from project root."
    exit 1
fi

log_info "✓ Manifests directory found"

# Prompt for configuration if not set
if [ "$REGISTRY" = "docker.io" ]; then
    read -p "Enter Docker registry (default: docker.io): " REGISTRY
    REGISTRY=${REGISTRY:-docker.io}
fi

if [ "$DOMAIN" = "atlantiplex.example.com" ]; then
    read -p "Enter domain name (default: atlantiplex.example.com): " DOMAIN
    DOMAIN=${DOMAIN:-atlantiplex.example.com}
fi

log_info "Configuration:"
log_info "  Registry: $REGISTRY"
log_info "  Domain: $DOMAIN"
log_info "  Image Tag: $IMAGE_TAG"

# Prompt for confirmation
read -p "Continue with deployment? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_warn "Deployment cancelled"
    exit 0
fi

# Create temporary directory for processed manifests
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

log_info "Processing manifests..."

# Copy manifests to temp directory and replace variables
cp k8s-optimized/*.yaml "$TEMP_DIR/" 2>/dev/null || true

# Replace placeholders in temp directory
sed -i "s|DOCKER_REGISTRY|$REGISTRY|g" "$TEMP_DIR"/*.yaml 2>/dev/null || true
sed -i "s|atlantiplex.example.com|$DOMAIN|g" "$TEMP_DIR"/*.yaml 2>/dev/null || true

log_info "✓ Manifests processed"

# Create namespace
log_info "Creating namespace..."
kubectl apply -f "$TEMP_DIR/00-namespace-config.yaml"
log_info "✓ Namespace created"

# Deploy databases
log_info "Deploying PostgreSQL..."
kubectl apply -f "$TEMP_DIR/01-postgres.yaml"

log_info "Deploying Redis..."
kubectl apply -f "$TEMP_DIR/02-redis.yaml"

# Wait for databases
log_info "Waiting for databases to be ready (max ${TIMEOUT}s)..."
if kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=${TIMEOUT}s 2>/dev/null; then
    log_info "✓ PostgreSQL is ready"
else
    log_warn "PostgreSQL readiness check timed out. Checking status..."
    kubectl get pods -n $NAMESPACE -l app=postgres
fi

if kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=${TIMEOUT}s 2>/dev/null; then
    log_info "✓ Redis is ready"
else
    log_warn "Redis readiness check timed out. Checking status..."
    kubectl get pods -n $NAMESPACE -l app=redis
fi

# Deploy applications
log_info "Deploying Flask backend..."
kubectl apply -f "$TEMP_DIR/03-flask-backend.yaml"

log_info "Deploying Stage server..."
kubectl apply -f "$TEMP_DIR/04-stage-server.yaml"

log_info "Deploying Frontend..."
kubectl apply -f "$TEMP_DIR/05-frontend.yaml"

# Deploy networking and policies
log_info "Deploying Ingress and networking policies..."
kubectl apply -f "$TEMP_DIR/06-ingress-networking.yaml"
kubectl apply -f "$TEMP_DIR/07-rbac-policies.yaml"

log_info "✓ All manifests applied"

# Wait for deployments
log_info "Waiting for deployments to be ready (max ${TIMEOUT}s)..."

for deployment in flask-backend stage-server frontend; do
    log_info "Waiting for $deployment..."
    if kubectl rollout status deployment/$deployment -n $NAMESPACE --timeout=${TIMEOUT}s 2>/dev/null; then
        log_info "✓ $deployment is ready"
    else
        log_warn "$deployment rollout status: check with 'kubectl get pods -n $NAMESPACE'"
    fi
done

# Print deployment summary
echo
log_info "=========================================="
log_info "Deployment Summary"
log_info "=========================================="

echo
log_info "Namespace: $NAMESPACE"
log_info "Domain: $DOMAIN"
log_info "Registry: $REGISTRY"

echo
log_info "Services:"
kubectl get svc -n $NAMESPACE --no-headers | awk '{print "  - " $1 " (" $3 ")"}'

echo
log_info "Deployments:"
kubectl get deployments -n $NAMESPACE --no-headers | awk '{print "  - " $1 " (replicas: " $2 "/" $3 ")"}'

echo
log_info "Databases:"
kubectl get statefulsets -n $NAMESPACE --no-headers | awk '{print "  - " $1 " (replicas: " $2 ")"}'

echo
log_info "Ingress:"
kubectl get ingress -n $NAMESPACE --no-headers | awk '{print "  - " $1 " (" $3 ")"}'

echo
log_info "HPA Status:"
kubectl get hpa -n $NAMESPACE --no-headers | awk '{print "  - " $1 " (min: " $2 ", max: " $3 ", current: " $4 ")"}'

echo
log_info "=========================================="
log_info "Next Steps:"
log_info "=========================================="
echo "1. Verify all pods are running:"
echo "   kubectl get pods -n $NAMESPACE"
echo
echo "2. Check pod logs:"
echo "   kubectl logs -n $NAMESPACE -l app=flask-backend -f"
echo
echo "3. Port forward for local testing:"
echo "   kubectl port-forward -n $NAMESPACE svc/frontend 8080:80"
echo
echo "4. Check ingress status:"
echo "   kubectl get ingress -n $NAMESPACE"
echo
echo "5. View deployment details:"
echo "   kubectl get all -n $NAMESPACE"
echo

log_info "✓ Deployment complete!"
