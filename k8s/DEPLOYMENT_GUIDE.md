# Kubernetes Deployment Guide for Atlantiplex

## Prerequisites

1. **Kubernetes Cluster** (v1.21+)
   - GKE, EKS, AKS, or self-managed
   - kubectl installed and configured
   - At least 4 nodes with 2CPU/4GB RAM each for production

2. **Container Images Built and Pushed**
   ```bash
   docker build -t your-registry/atlantiplex-stage:latest -f matrix-studio/web/stage/Dockerfile .
   docker build -t your-registry/atlantiplex-flask:latest -f matrix-studio/Dockerfile.python .
   docker build -t your-registry/atlantiplex-frontend:latest -f AtlantiplexStudio/Dockerfile .
   docker build -t your-registry/atlantiplex-gateway:latest -f gateway/Dockerfile .
   
   docker push your-registry/atlantiplex-stage:latest
   docker push your-registry/atlantiplex-flask:latest
   docker push your-registry/atlantiplex-frontend:latest
   docker push your-registry/atlantiplex-gateway:latest
   ```

3. **Docker Registry Credentials** (if using private registry)
   ```bash
   kubectl create secret docker-registry regcred \
     --docker-server=<your-registry> \
     --docker-username=<username> \
     --docker-password=<password> \
     --docker-email=<email> \
     -n atlantiplex
   ```

4. **Storage Class Available**
   - For local development: Use `minikube` or `kind` with local-path provisioner
   - For cloud: GKE/EKS/AKS automatically provide storage classes

---

## Deployment Steps

### Step 1: Update Configuration Files

Edit the manifests before deploying:

#### 1a. Update Secrets (`k8s/02-secrets.yaml`)
```bash
# Replace placeholder values with actual production secrets
sed -i 's/CHANGE_ME_PRODUCTION_PASSWORD/YOUR_ACTUAL_DB_PASSWORD/g' k8s/02-secrets.yaml
sed -i 's/CHANGE_ME_REDIS_PASSWORD/YOUR_ACTUAL_REDIS_PASSWORD/g' k8s/02-secrets.yaml
sed -i 's/CHANGE_ME_JWT_SECRET_KEY/YOUR_ACTUAL_JWT_SECRET/g' k8s/02-secrets.yaml
# ... repeat for other secrets
```

OR use a .env file:
```bash
kubectl create secret generic atlantiplex-secrets \
  --from-literal=DB_PASSWORD="$DB_PASSWORD" \
  --from-literal=REDIS_PASSWORD="$REDIS_PASSWORD" \
  --from-literal=JWT_SECRET="$JWT_SECRET" \
  --from-literal=JWT_REFRESH_SECRET="$JWT_REFRESH_SECRET" \
  --from-literal=STRIPE_SECRET_KEY="$STRIPE_SECRET_KEY" \
  --from-literal=STRIPE_PUBLISHABLE_KEY="$STRIPE_PUBLISHABLE_KEY" \
  --from-literal=STRIPE_WEBHOOK_SECRET="$STRIPE_WEBHOOK_SECRET" \
  --from-literal=DATABASE_URL="postgresql://atlantiplex:$DB_PASSWORD@postgres:5432/atlantiplex" \
  --from-literal=REDIS_URL="redis://:$REDIS_PASSWORD@redis:6379/0" \
  -n atlantiplex
```

#### 1b. Update ConfigMap (`k8s/01-namespace-configmap.yaml`)
```yaml
data:
  CORS_ORIGIN: "https://yourdomain.com"
  API_URL: "https://api.yourdomain.com"
```

#### 1c. Update TLS Secret (`k8s/02-secrets.yaml`)
```bash
kubectl create secret tls atlantiplex-tls \
  --cert=/path/to/tls.crt \
  --key=/path/to/tls.key \
  -n atlantiplex
```

#### 1d. Update Image Names (`k8s/05-node-deployments.yaml`, `k8s/06-flask-deployment.yaml`, `k8s/07-frontend-ingress.yaml`)
```bash
# Replace image references
sed -i 's|atlantiplex-stage:latest|your-registry/atlantiplex-stage:v1.0|g' k8s/*.yaml
sed -i 's|atlantiplex-flask:latest|your-registry/atlantiplex-flask:v1.0|g' k8s/*.yaml
sed -i 's|atlantiplex-frontend:latest|your-registry/atlantiplex-frontend:v1.0|g' k8s/*.yaml
sed -i 's|atlantiplex-gateway:latest|your-registry/atlantiplex-gateway:v1.0|g' k8s/*.yaml
```

### Step 2: Deploy Manifests in Order

```bash
# 1. Create namespace and ConfigMaps
kubectl apply -f k8s/01-namespace-configmap.yaml

# 2. Create secrets (update values first!)
kubectl apply -f k8s/02-secrets.yaml

# 3. Deploy databases (will wait for PVC provisioning)
kubectl apply -f k8s/03-postgres.yaml
kubectl apply -f k8s/04-redis.yaml

# Wait for postgres and redis to be ready
kubectl wait --for=condition=Ready pod -l app=postgres -n atlantiplex --timeout=300s
kubectl wait --for=condition=Ready pod -l app=redis -n atlantiplex --timeout=300s

# 4. Deploy backend services
kubectl apply -f k8s/05-node-deployments.yaml
kubectl apply -f k8s/06-flask-deployment.yaml

# 5. Deploy frontend and ingress
kubectl apply -f k8s/07-frontend-ingress.yaml

# Optional: Use Kubernetes Ingress Controller instead of LoadBalancer
# kubectl apply -f k8s/08-ingress-nginx.yaml
```

### Step 3: Verify Deployment

```bash
# Check namespace
kubectl get ns

# Check pods
kubectl get pods -n atlantiplex

# Check services
kubectl get svc -n atlantiplex

# Get LoadBalancer IP (wait for EXTERNAL-IP)
kubectl get svc nginx-ingress -n atlantiplex -w

# Check pod logs
kubectl logs -f deployment/stage-server -n atlantiplex
kubectl logs -f deployment/flask-backend -n atlantiplex
kubectl logs -f deployment/frontend -n atlantiplex

# Check events
kubectl get events -n atlantiplex --sort-by='.lastTimestamp'
```

### Step 4: Configure DNS

Once LoadBalancer has external IP:
```bash
# Get external IP
EXTERNAL_IP=$(kubectl get svc nginx-ingress -n atlantiplex -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Point your domain to this IP in your DNS provider
# atlantiplex.example.com → $EXTERNAL_IP
# api.atlantiplex.example.com → $EXTERNAL_IP
# *.atlantiplex.example.com → $EXTERNAL_IP
```

### Step 5: Scale Deployments (Optional)

```bash
# Scale stage-server to 3 replicas
kubectl scale deployment stage-server --replicas=3 -n atlantiplex

# Scale flask-backend to 3 replicas
kubectl scale deployment flask-backend --replicas=3 -n atlantiplex

# Scale frontend to 2 replicas (already set)
kubectl get deployment -n atlantiplex
```

---

## Monitoring and Management

### View Logs
```bash
# All pods in namespace
kubectl logs -f -n atlantiplex --all-containers=true -l tier=backend

# Specific service
kubectl logs -f deployment/stage-server -n atlantiplex

# Previous crash logs
kubectl logs --previous pod/stage-server-xxxxx -n atlantiplex
```

### Port Forwarding (for debugging)
```bash
# Forward postgres locally
kubectl port-forward svc/postgres 5432:5432 -n atlantiplex

# Forward redis locally
kubectl port-forward svc/redis 6379:6379 -n atlantiplex

# Forward frontend locally
kubectl port-forward svc/frontend 8080:80 -n atlantiplex
```

### Execute Commands in Pod
```bash
# SSH into pod
kubectl exec -it pod/stage-server-xxxxx -n atlantiplex -- /bin/sh

# Run migration
kubectl exec pod/stage-server-xxxxx -n atlantiplex -- npm run migrate
```

### Resource Usage
```bash
# CPU and memory per pod
kubectl top pods -n atlantiplex

# CPU and memory per node
kubectl top nodes

# Detailed resource requests/limits
kubectl describe nodes
```

---

## Troubleshooting

### Pod stuck in Pending
```bash
kubectl describe pod <pod-name> -n atlantiplex
# Check: PVC binding, storage class, resource requests vs available
```

### CrashLoopBackOff
```bash
kubectl logs --previous pod/<pod-name> -n atlantiplex
# Check logs for startup errors
```

### Service not reachable
```bash
# Check service endpoints
kubectl get endpoints svc/stage-server -n atlantiplex

# Check network policies (if any)
kubectl get networkpolicies -n atlantiplex

# Test connectivity between pods
kubectl run -it debug --image=alpine -n atlantiplex -- sh
  wget -O- http://stage-server:9001/health
```

### Database connection issues
```bash
# Verify postgres is running
kubectl exec -it pod/postgres-0 -n atlantiplex -- psql -U atlantiplex -d atlantiplex -c "SELECT 1"

# Check DATABASE_URL format
kubectl get secret atlantiplex-secrets -n atlantiplex -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

---

## Production Best Practices

### 1. Use Sealed Secrets for Sensitive Data
```bash
# Install sealed-secrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.18.0/controller.yaml

# Create sealed secret
echo -n mypassword | kubectl create secret generic mysecret --dry-run=client --from-file=/dev/stdin -o yaml | kubeseal -f -
```

### 2. Enable Horizontal Pod Autoscaling
```bash
kubectl autoscale deployment stage-server --min=2 --max=5 -n atlantiplex
kubectl autoscale deployment flask-backend --min=2 --max=5 -n atlantiplex
```

### 3. Set Resource Quotas
```bash
kubectl create quota compute-quota --hard=cpu=10,memory=20Gi -n atlantiplex
```

### 4. Use Network Policies
```bash
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: atlantiplex
spec:
  podSelector: {}
  policyTypes:
  - Ingress
EOF
```

### 5. Enable Ingress Controller with TLS
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@atlantiplex.example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### 6. Backup Database Regularly
```bash
# Backup postgres
kubectl exec pod/postgres-0 -n atlantiplex -- pg_dump -U atlantiplex atlantiplex > backup.sql

# Restore from backup
kubectl cp backup.sql atlantiplex/postgres-0:/tmp/
kubectl exec -it pod/postgres-0 -n atlantiplex -- psql -U atlantiplex atlantiplex < /tmp/backup.sql
```

---

## Cleanup

```bash
# Delete all resources in namespace
kubectl delete namespace atlantiplex

# Delete specific deployment
kubectl delete deployment stage-server -n atlantiplex

# Delete specific service
kubectl delete svc frontend -n atlantiplex
```

---

## Manifest File Organization

```
k8s/
├── 01-namespace-configmap.yaml    # Namespace + ConfigMaps
├── 02-secrets.yaml               # Secrets (UPDATE BEFORE DEPLOY)
├── 03-postgres.yaml              # PostgreSQL StatefulSet
├── 04-redis.yaml                 # Redis StatefulSet
├── 05-node-deployments.yaml      # Stage-server + Gateway Deployments
├── 06-flask-deployment.yaml      # Flask Backend Deployment
├── 07-frontend-ingress.yaml      # Frontend + nginx Ingress
├── 08-ingress-nginx.yaml         # Kubernetes Ingress (optional alternative)
└── DEPLOYMENT_GUIDE.md           # This file
```

---

## Quick Deploy Script

```bash
#!/bin/bash
set -e

# Load environment variables
source .env.production

# Create namespace and apply manifests
kubectl apply -f k8s/01-namespace-configmap.yaml

# Create secrets from environment
kubectl create secret generic atlantiplex-secrets \
  --from-literal=DB_PASSWORD="$DB_PASSWORD" \
  --from-literal=REDIS_PASSWORD="$REDIS_PASSWORD" \
  --from-literal=JWT_SECRET="$JWT_SECRET" \
  --from-literal=JWT_REFRESH_SECRET="$JWT_REFRESH_SECRET" \
  --from-literal=STRIPE_SECRET_KEY="$STRIPE_SECRET_KEY" \
  --from-literal=STRIPE_PUBLISHABLE_KEY="$STRIPE_PUBLISHABLE_KEY" \
  --from-literal=STRIPE_WEBHOOK_SECRET="$STRIPE_WEBHOOK_SECRET" \
  --from-literal=DATABASE_URL="postgresql://atlantiplex:$DB_PASSWORD@postgres:5432/atlantiplex" \
  --from-literal=REDIS_URL="redis://:$REDIS_PASSWORD@redis:6379/0" \
  -n atlantiplex --dry-run=client -o yaml | kubectl apply -f -

# Deploy all services
kubectl apply -f k8s/03-postgres.yaml
kubectl apply -f k8s/04-redis.yaml
kubectl apply -f k8s/05-node-deployments.yaml
kubectl apply -f k8s/06-flask-deployment.yaml
kubectl apply -f k8s/07-frontend-ingress.yaml

echo "Deployment complete!"
echo "Check status: kubectl get all -n atlantiplex"
```

---

**Last Updated:** 2024
**Kubernetes Version:** 1.21+
**Author:** Atlantiplex Team
