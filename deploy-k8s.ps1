# Atlantiplex Kubernetes Deployment Script (PowerShell)
# Usage: .\deploy-k8s.ps1 -Environment staging -Registry docker.io/atlantiplex -ImageTag latest

param(
    [string]$Environment = "staging",
    [string]$Registry = "docker.io/atlantiplex",
    [string]$ImageTag = "latest"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Atlantiplex Kubernetes Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Environment: $Environment"
Write-Host "Registry: $Registry"
Write-Host "Image Tag: $ImageTag"
Write-Host "==========================================" -ForegroundColor Cyan

# Functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Step 1: Check prerequisites
Write-Info "Checking prerequisites..."

try {
    $null = kubectl version --client --short
    Write-Info "kubectl found."
} catch {
    Write-Error "kubectl not found. Please install kubectl."
    exit 1
}

try {
    $clusterName = kubectl config current-context
    Write-Info "Connected to cluster: $clusterName"
} catch {
    Write-Error "Failed to connect to Kubernetes cluster."
    exit 1
}

# Step 2: Create namespace
Write-Info "Creating namespace..."
kubectl create namespace atlantiplex --dry-run=client -o yaml | kubectl apply -f -

# Step 3: Apply configuration
Write-Info "Applying ConfigMaps..."
kubectl apply -f k8s/01-namespace-configmap.yaml

# Step 4: Verify secrets exist
Write-Info "Checking secrets..."
try {
    $null = kubectl get secret atlantiplex-secrets -n atlantiplex
    Write-Warn "Secrets already exist. Skipping secret creation."
    Write-Warn "To update secrets: kubectl delete secret atlantiplex-secrets -n atlantiplex"
} catch {
    Write-Error "Secrets not found. Please create them first:"
    Write-Error "kubectl create secret generic atlantiplex-secrets --from-literal=DB_PASSWORD='...' -n atlantiplex"
    exit 1
}

# Step 5: Deploy databases
Write-Info "Deploying PostgreSQL..."
kubectl apply -f k8s/03-postgres.yaml

Write-Info "Deploying Redis..."
kubectl apply -f k8s/04-redis.yaml

# Step 6: Wait for databases (optional)
Write-Info "Deploying Node.js services..."
kubectl apply -f k8s/05-node-deployments.yaml

Write-Info "Deploying Flask backend..."
kubectl apply -f k8s/06-flask-deployment.yaml

Write-Info "Deploying frontend and ingress..."
kubectl apply -f k8s/07-frontend-ingress.yaml

# Step 7: Summary
Write-Info "Deployment initiated!"
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Monitor deployment status:"
Write-Host "   kubectl get pods -n atlantiplex -w" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Check service status:"
Write-Host "   kubectl get svc -n atlantiplex" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Get external IP (wait for LoadBalancer):"
Write-Host "   kubectl get svc nginx-ingress -n atlantiplex" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. View logs:"
Write-Host "   kubectl logs -f deployment/stage-server -n atlantiplex" -ForegroundColor Yellow
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Print deployment status
Write-Info "Current deployment status:"
kubectl get all -n atlantiplex --no-headers
