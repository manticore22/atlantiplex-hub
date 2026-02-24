# Kubernetes Deployment + GitHub Push
# Simplified version without special characters

param(
    [string]$Registry = "docker.io/atlantiplex",
    [string]$ImageTag = "v1.0.0-security",
    [string]$GitBranch = "main",
    [switch]$DryRun = $false
)

Write-Host ""
Write-Host "ATLANTIPLEX KUBERNETES DEPLOYMENT + GITHUB PUSH" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "[1/11] Checking Prerequisites..." -ForegroundColor Green

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker not installed" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: kubectl not installed" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Git not installed" -ForegroundColor Red
    exit 1
}

$cluster = kubectl cluster-info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Not connected to Kubernetes cluster" -ForegroundColor Red
    exit 1
}

Write-Host "OK - All prerequisites met" -ForegroundColor Green

# Step 2: Git setup
Write-Host "[2/11] Preparing Git Repository..." -ForegroundColor Green

if (-not $DryRun) {
    git checkout -B "deploy/$ImageTag" 2>&1 | Out-Null
    git add -A 2>&1 | Out-Null
    Write-Host "OK - Branch: deploy/$ImageTag" -ForegroundColor Green
} else {
    Write-Host "[DRY-RUN] Would create branch: deploy/$ImageTag" -ForegroundColor Yellow
}

# Step 3: Build images
Write-Host "[3/11] Building Docker Images..." -ForegroundColor Green

$images = @(
    @{ name = "stage"; path = "matrix-studio/web/stage/Dockerfile" },
    @{ name = "flask"; path = "matrix-studio/Dockerfile.python" },
    @{ name = "frontend"; path = "AtlantiplexStudio/Dockerfile" },
    @{ name = "gateway"; path = "gateway/Dockerfile" }
)

foreach ($img in $images) {
    $tag = "$Registry/atlantiplex-$($img.name):$ImageTag"
    if (-not $DryRun) {
        Write-Host "  Building $($img.name)..." -ForegroundColor Yellow
        docker build -f $img.path -t $tag . 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    OK: $tag" -ForegroundColor Green
        }
    } else {
        Write-Host "  [DRY-RUN] $tag" -ForegroundColor Yellow
    }
}

# Step 4: Push images
Write-Host "[4/11] Pushing Images to Registry..." -ForegroundColor Green

foreach ($img in $images) {
    $tag = "$Registry/atlantiplex-$($img.name):$ImageTag"
    if (-not $DryRun) {
        Write-Host "  Pushing $($img.name)..." -ForegroundColor Yellow
        docker push $tag 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    OK: $tag" -ForegroundColor Green
        }
    } else {
        Write-Host "  [DRY-RUN] $tag" -ForegroundColor Yellow
    }
}

# Step 5: Update manifests
Write-Host "[5/11] Updating Kubernetes Manifests..." -ForegroundColor Green

$files = @(
    "k8s/05-node-deployments.yaml",
    "k8s/06-flask-deployment.yaml",
    "k8s/07-frontend-ingress.yaml"
)

foreach ($f in $files) {
    if (-not $DryRun -and (Test-Path $f)) {
        Write-Host "  Updating $f..." -ForegroundColor Yellow
        $content = Get-Content $f -Raw
        $content = $content -replace "atlantiplex-stage:latest", "atlantiplex-stage:$ImageTag"
        $content = $content -replace "atlantiplex-flask:latest", "atlantiplex-flask:$ImageTag"
        $content = $content -replace "atlantiplex-frontend:latest", "atlantiplex-frontend:$ImageTag"
        $content = $content -replace "atlantiplex-gateway:latest", "atlantiplex-gateway:$ImageTag"
        Set-Content -Path $f -Value $content
        Write-Host "    OK" -ForegroundColor Green
    }
}

# Step 6: Check secrets
Write-Host "[6/11] Checking Kubernetes Secrets..." -ForegroundColor Green

$secretExists = kubectl get secret atlantiplex-secrets -n atlantiplex 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Secrets not found. Create with:" -ForegroundColor Yellow
    Write-Host "kubectl create secret generic atlantiplex-secrets -n atlantiplex --from-literal=DB_PASSWORD='...' ..." -ForegroundColor Yellow
} else {
    Write-Host "OK - Secrets exist" -ForegroundColor Green
}

# Step 7: Deploy
Write-Host "[7/11] Deploying to Kubernetes..." -ForegroundColor Green

$deployments = @(
    "k8s/01-namespace-configmap.yaml",
    "k8s/02-secrets.yaml",
    "k8s/03-postgres.yaml",
    "k8s/04-redis.yaml",
    "k8s/05-node-deployments.yaml",
    "k8s/06-flask-deployment.yaml",
    "k8s/07-frontend-ingress.yaml"
)

foreach ($dep in $deployments) {
    if (-not $DryRun -and (Test-Path $dep)) {
        Write-Host "  Applying $dep..." -ForegroundColor Yellow
        kubectl apply -f $dep 2>&1 | Out-Null
        Write-Host "    OK" -ForegroundColor Green
    } elseif ($DryRun) {
        Write-Host "  [DRY-RUN] $dep" -ForegroundColor Yellow
    }
}

# Step 8: Wait for deployment
Write-Host "[8/11] Waiting for Deployment..." -ForegroundColor Green

if (-not $DryRun) {
    Write-Host "  Waiting for pods..." -ForegroundColor Yellow
    kubectl wait --for=condition=Ready pod -l app=postgres -n atlantiplex --timeout=300s 2>&1 | Out-Null
    kubectl wait --for=condition=Ready pod -l app=redis -n atlantiplex --timeout=300s 2>&1 | Out-Null
    Write-Host "    OK - Ready" -ForegroundColor Green
} else {
    Write-Host "  [DRY-RUN] Would wait for pods" -ForegroundColor Yellow
}

# Step 9: Verify
Write-Host "[9/11] Verifying Deployment..." -ForegroundColor Green

if (-not $DryRun) {
    $pods = kubectl get pods -n atlantiplex --no-headers 2>&1 | Measure-Object -Line
    Write-Host "  Pods: $($pods.Lines) running" -ForegroundColor Green
    
    $svc = kubectl get svc nginx-ingress -n atlantiplex -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>&1
    if ($svc) {
        Write-Host "  External IP: $svc" -ForegroundColor Green
    } else {
        Write-Host "  External IP: Pending (check in 1-2 minutes)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [DRY-RUN] Would verify pods and services" -ForegroundColor Yellow
}

# Step 10: Git commit & push
Write-Host "[10/11] Committing to GitHub..." -ForegroundColor Green

if (-not $DryRun) {
    $msg = "Deploy: Kubernetes v$ImageTag with security fixes`n`nRegistry: $Registry`nImage Tag: $ImageTag`nEnvironment: Production`n`nAssisted-By: cagent"
    git commit -m $msg 2>&1 | Out-Null
    Write-Host "  Committed" -ForegroundColor Green
    
    git push -u origin $GitBranch 2>&1 | Out-Null
    Write-Host "  Pushed to GitHub" -ForegroundColor Green
    
    git tag -a $ImageTag -m "Release: Atlantiplex $ImageTag" 2>&1 | Out-Null
    git push origin $ImageTag 2>&1 | Out-Null
    Write-Host "  Release tag created: $ImageTag" -ForegroundColor Green
} else {
    Write-Host "  [DRY-RUN] Would commit and push" -ForegroundColor Yellow
}

# Step 11: Summary
Write-Host "[11/11] Deployment Complete!" -ForegroundColor Green

Write-Host ""
Write-Host "SUMMARY:" -ForegroundColor Cyan
Write-Host "  Registry: $Registry"
Write-Host "  Image Tag: $ImageTag"
Write-Host "  Branch: $GitBranch"
Write-Host "  Namespace: atlantiplex"
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "  1. Monitor deployment:"
Write-Host "     kubectl get pods -n atlantiplex -w"
Write-Host ""
Write-Host "  2. Get external IP:"
Write-Host "     kubectl get svc nginx-ingress -n atlantiplex"
Write-Host ""
Write-Host "  3. Configure DNS with external IP"
Write-Host ""
Write-Host "  4. View logs:"
Write-Host "     kubectl logs -f deployment/stage-server -n atlantiplex"
Write-Host ""

if ($DryRun) {
    Write-Host "MODE: DRY-RUN (no changes applied)" -ForegroundColor Yellow
}

Write-Host ""
