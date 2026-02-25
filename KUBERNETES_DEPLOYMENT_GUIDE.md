# KUBERNETES DEPLOYMENT + GITHUB PUSH GUIDE

## Quick Start (3 Steps)

### Step 1: Configure GitHub & Registry Credentials

```bash
# Configure git (if not already done)
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Docker login (if using private registry)
docker login docker.io -u yourregistry
```

### Step 2: Configure Kubernetes Secrets

```bash
# Create secrets with your production values
kubectl create secret generic atlantiplex-secrets -n atlantiplex \
  --from-literal=DB_PASSWORD="strong_password_min_16_chars" \
  --from-literal=REDIS_PASSWORD="strong_password_min_16_chars" \
  --from-literal=JWT_SECRET="random_string_min_32_chars" \
  --from-literal=JWT_REFRESH_SECRET="random_string_min_32_chars" \
  --from-literal=STRIPE_SECRET_KEY="sk_live_your_key" \
  --from-literal=STRIPE_PUBLISHABLE_KEY="pk_live_your_key" \
  --from-literal=STRIPE_WEBHOOK_SECRET="whsec_your_secret" \
  --from-literal=DATABASE_URL="postgresql://atlantiplex:password@postgres:5432/atlantiplex?sslmode=require" \
  --from-literal=REDIS_URL="redis://:password@redis:6379/0"
```

### Step 3: Run Deployment Script

```bash
# DRY-RUN first (see what would happen)
powershell -ExecutionPolicy Bypass -File ./deploy-to-k8s-and-github.ps1 `
  -Registry "docker.io/atlantiplex" `
  -ImageTag "v1.0.0" `
  -DryRun

# Real deployment
powershell -ExecutionPolicy Bypass -File ./deploy-to-k8s-and-github.ps1 `
  -Registry "docker.io/atlantiplex" `
  -ImageTag "v1.0.0" `
  -GitBranch "main"
```

---

## What the Script Does

### Phase 1: Validation (Step 1)
- Checks Docker installation
- Checks kubectl installation
- Checks Git installation
- Verifies Kubernetes cluster connection

### Phase 2: Image Build (Steps 2-4)
- Creates deploy branch in Git
- Builds Docker images:
  - atlantiplex-stage (Node.js API)
  - atlantiplex-flask (Python backend)
  - atlantiplex-frontend (nginx frontend)
  - atlantiplex-gateway (API gateway)
- Pushes all images to registry (docker.io/atlantiplex)

### Phase 3: Kubernetes Deployment (Steps 5-9)
- Updates manifests with new image tags
- Verifies secrets exist
- Deploys all Kubernetes resources:
  - Namespace & ConfigMaps
  - PostgreSQL StatefulSet
  - Redis StatefulSet
  - Node.js services (2 replicas each)
  - Flask backend (2 replicas)
  - Frontend (2 replicas)
  - nginx Ingress with LoadBalancer
- Waits for all pods to be ready

### Phase 4: GitHub Push (Step 10)
- Commits all changes with deployment message
- Pushes to main branch
- Creates release tag (v1.0.0)
- Pushes tag to GitHub

---

## Manual Deployment (If Script Fails)

### 1. Build Images

```bash
# Stage Server
docker build -f matrix-studio/web/stage/Dockerfile \
  -t docker.io/atlantiplex/atlantiplex-stage:v1.0.0 .
docker push docker.io/atlantiplex/atlantiplex-stage:v1.0.0

# Flask Backend
docker build -f matrix-studio/Dockerfile.python \
  -t docker.io/atlantiplex/atlantiplex-flask:v1.0.0 .
docker push docker.io/atlantiplex/atlantiplex-flask:v1.0.0

# Frontend
docker build -f AtlantiplexStudio/Dockerfile \
  -t docker.io/atlantiplex/atlantiplex-frontend:v1.0.0 .
docker push docker.io/atlantiplex/atlantiplex-frontend:v1.0.0

# Gateway
docker build -f gateway/Dockerfile \
  -t docker.io/atlantiplex/atlantiplex-gateway:v1.0.0 .
docker push docker.io/atlantiplex/atlantiplex-gateway:v1.0.0
```

### 2. Update Manifests

Replace image tags in k8s files:
- `atlantiplex-stage:latest` → `atlantiplex-stage:v1.0.0`
- `atlantiplex-flask:latest` → `atlantiplex-flask:v1.0.0`
- `atlantiplex-frontend:latest` → `atlantiplex-frontend:v1.0.0`
- `atlantiplex-gateway:latest` → `atlantiplex-gateway:v1.0.0`

### 3. Deploy

```bash
# Create namespace & config
kubectl apply -f k8s/01-namespace-configmap.yaml

# Create secrets (if not already done)
kubectl apply -f k8s/02-secrets.yaml

# Deploy databases
kubectl apply -f k8s/03-postgres.yaml
kubectl apply -f k8s/04-redis.yaml

# Wait for databases
kubectl wait --for=condition=Ready pod -l app=postgres -n atlantiplex --timeout=300s
kubectl wait --for=condition=Ready pod -l app=redis -n atlantiplex --timeout=300s

# Deploy applications
kubectl apply -f k8s/05-node-deployments.yaml
kubectl apply -f k8s/06-flask-deployment.yaml
kubectl apply -f k8s/07-frontend-ingress.yaml

# Wait for all ready
kubectl wait --for=condition=Ready pod -n atlantiplex --all --timeout=600s
```

### 4. Push to GitHub

```bash
# Create deployment branch
git checkout -B deploy/v1.0.0

# Stage changes
git add -A

# Commit
git commit -m "Deploy: Kubernetes v1.0.0 with security fixes

Registry: docker.io/atlantiplex
Image Tag: v1.0.0
Environment: Production
Security: All vulnerabilities fixed

Assisted-By: cagent"

# Push
git push -u origin main

# Create release tag
git tag -a v1.0.0 -m "Release: Atlantiplex v1.0.0"
git push origin v1.0.0
```

---

## Verify Deployment

```bash
# Check pods
kubectl get pods -n atlantiplex

# Expected output:
# NAME                              READY   STATUS    RESTARTS
# postgres-0                        1/1     Running   0
# redis-0                           1/1     Running   0
# stage-server-xxx                  1/1     Running   0
# stage-server-yyy                  1/1     Running   0
# flask-backend-xxx                 1/1     Running   0
# flask-backend-yyy                 1/1     Running   0
# frontend-xxx                      1/1     Running   0
# frontend-yyy                      1/1     Running   0
# nginx-ingress-xxx                 1/1     Running   0
# nginx-ingress-yyy                 1/1     Running   0

# Check services
kubectl get svc -n atlantiplex

# Get external IP
kubectl get svc nginx-ingress -n atlantiplex -o wide

# Check logs
kubectl logs -f deployment/stage-server -n atlantiplex

# Describe deployment
kubectl describe deployment stage-server -n atlantiplex

# Check events
kubectl get events -n atlantiplex
```

---

## Configure DNS

Once you have the external IP:

```bash
# Get external IP
EXTERNAL_IP=$(kubectl get svc nginx-ingress -n atlantiplex -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo $EXTERNAL_IP

# Point these DNS records to the external IP:
# atlantiplex.example.com         → EXTERNAL_IP
# api.atlantiplex.example.com     → EXTERNAL_IP
# *.atlantiplex.example.com       → EXTERNAL_IP
```

---

## Troubleshooting

### Pod stuck in Pending
```bash
kubectl describe pod <pod-name> -n atlantiplex
# Check: PVC binding, storage class, resource limits
```

### CrashLoopBackOff
```bash
kubectl logs --previous pod/<pod-name> -n atlantiplex
# Check: Application startup errors
```

### Service without external IP
```bash
# Check if LoadBalancer has external IP assigned
kubectl describe svc nginx-ingress -n atlantiplex

# For local Kubernetes (Docker Desktop, Minikube):
kubectl patch svc nginx-ingress -p '{"spec":{"type":"NodePort"}}' -n atlantiplex
kubectl get svc nginx-ingress -n atlantiplex
# Use NodePort instead
```

### Database connection errors
```bash
# Check postgres is running
kubectl exec -it pod/postgres-0 -n atlantiplex -- psql -U atlantiplex -d atlantiplex

# Check redis
kubectl exec -it pod/redis-0 -n atlantiplex -- redis-cli
```

---

## Rollback

```bash
# Revert to previous deployment
kubectl rollout undo deployment/stage-server -n atlantiplex
kubectl rollout undo deployment/flask-backend -n atlantiplex
kubectl rollout undo deployment/frontend -n atlantiplex

# Check rollout history
kubectl rollout history deployment/stage-server -n atlantiplex

# Rollback to specific revision
kubectl rollout undo deployment/stage-server -n atlantiplex --to-revision=1
```

---

## Monitoring

```bash
# Watch deployments
kubectl get deployments -n atlantiplex -w

# Monitor resources
kubectl top pods -n atlantiplex
kubectl top nodes

# Stream logs from all pods
kubectl logs -f -l tier=backend -n atlantiplex --all-containers

# Port forward for debugging
kubectl port-forward svc/postgres 5432:5432 -n atlantiplex
kubectl port-forward svc/redis 6379:6379 -n atlantiplex
```

---

## Production Checklist

- [ ] Kubernetes cluster is running and accessible
- [ ] kubectl is installed and configured
- [ ] Docker credentials configured (if using private registry)
- [ ] GitHub credentials configured
- [ ] All secrets created in Kubernetes
- [ ] DNS records prepared (ready to point to external IP)
- [ ] Backup of .env and secrets taken
- [ ] TLS certificates prepared (or Let's Encrypt configured)
- [ ] Monitoring and alerting configured
- [ ] Disaster recovery plan reviewed

---

## Security Verification

```bash
# Verify non-root execution
kubectl exec pod/stage-server-xxx -n atlantiplex -- whoami
# Should output: nodejs (not root)

# Check security context
kubectl get pod <pod-name> -n atlantiplex -o jsonpath='{.spec.securityContext}'

# Verify network policies (if configured)
kubectl get networkpolicies -n atlantiplex
```

---

## GitHub References

After deployment, your GitHub repository should have:

- Main branch with all code and configuration
- Release tag (e.g., v1.0.0) marking the deployment
- Deployment branch (e.g., deploy/v1.0.0) with manifest updates
- All security fixes committed and pushed

Example commit message:
```
Deploy: Kubernetes v1.0.0 with security fixes

Registry: docker.io/atlantiplex
Image Tag: v1.0.0
Environment: Production
Security: All vulnerabilities fixed

Assisted-By: cagent
```

---

## Timeline

| Step | Duration | Task |
|------|----------|------|
| 1 | 5 min | Configure credentials |
| 2 | 5 min | Create secrets |
| 3 | 10 min | Run deployment script |
| 4 | 5 min | Verify deployment |
| 5 | 5 min | Configure DNS |
| **Total** | **30 min** | **Production ready** |

---

## Support

- Kubernetes docs: https://kubernetes.io/docs/
- kubectl cheat sheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- Docker docs: https://docs.docker.com/
- GitHub docs: https://docs.github.com/

---

**Status:** Ready for deployment
**Last Updated:** 2024
**Next Step:** Run the deployment script!
