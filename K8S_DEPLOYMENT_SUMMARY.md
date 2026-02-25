# Kubernetes Deployment Summary

## ✅ Complete Kubernetes Setup Generated

All production-ready Kubernetes manifests have been created and organized in `./k8s/` directory.

---

## What Was Created

### Manifests (8 files)
1. **01-namespace-configmap.yaml** (5.4 KB)
   - Creates `atlantiplex` namespace
   - Non-sensitive configuration (NODE_ENV, LOG_LEVEL, CORS_ORIGIN, etc.)
   - nginx configuration embedded for ingress controller

2. **02-secrets.yaml** (1.4 KB) — ⚠️ **UPDATE BEFORE DEPLOYING**
   - Database credentials
   - JWT secrets
   - Stripe API keys
   - TLS certificate (placeholder)
   - Replace all `CHANGE_ME_*` values with production secrets

3. **03-postgres.yaml** (3.0 KB)
   - PostgreSQL StatefulSet (1 replica)
   - 50Gi PersistentVolumeClaim
   - Health checks (liveness + readiness)
   - Security context (non-root, capability dropping)

4. **04-redis.yaml** (2.7 KB)
   - Redis StatefulSet (1 replica)
   - 10Gi PersistentVolumeClaim
   - AOF persistence enabled
   - LRU eviction policy configured

5. **05-node-deployments.yaml** (6.4 KB)
   - Stage-Server (Node.js, 2 replicas)
   - Gateway (Node.js, 2 replicas)
   - Pod anti-affinity for HA
   - Resource requests/limits
   - Environment variables from Secrets/ConfigMaps

6. **06-flask-deployment.yaml** (4.0 KB)
   - Flask Backend (Python, 2 replicas)
   - Connected to PostgreSQL + Redis
   - Health checks on `/api/health`
   - Logging configured

7. **07-frontend-ingress.yaml** (5.5 KB)
   - Frontend nginx deployment (2 replicas)
   - nginx Ingress Controller deployment (2 replicas)
   - LoadBalancer service for external access
   - Read-only filesystem for security

8. **08-ingress-nginx.yaml** (1.3 KB)
   - Alternative Kubernetes Ingress resource
   - cert-manager integration for automatic TLS
   - Use if your cluster has nginx-ingress controller

### Documentation (3 files)
- **DEPLOYMENT_GUIDE.md** (11.6 KB) - Step-by-step deployment instructions
- **README.md** (12.4 KB) - Architecture overview and quick reference
- **This file**

### Deployment Scripts (2 files)
- **deploy-k8s.sh** - Bash script for Linux/Mac
- **deploy-k8s.ps1** - PowerShell script for Windows

---

## Architecture

```
Kubernetes Cluster (atlantiplex namespace)

                    ┌─────────────────────┐
                    │   LoadBalancer      │ (External IP)
                    │   Port 80 → 443     │
                    └──────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │ nginx Ingress      │ 2 replicas
                    │ (HTTPS, routing)   │
                    └─────────┬──────────┘
                    │         │         │
        ┌───────────▼────┐ ┌──▼────────┴──┐ ┌──────────────┐
        │  Frontend      │ │ Stage-Server │ │ Flask        │
        │  (nginx SPA)   │ │ (Node.js)    │ │ (Python)     │
        │  2 replicas    │ │ 2 replicas   │ │ 2 replicas   │
        └────────────────┘ └──────┬───────┘ └──────┬───────┘
                                  │                 │
                          ┌───────┴─────────────────┘
                          │
                    ┌─────▼──────────┐
                    │  PostgreSQL    │ StatefulSet, 50Gi PVC
                    │  (1 replica)   │
                    └────────────────┘
                    
                    ┌─────────────────┐
                    │  Redis          │ StatefulSet, 10Gi PVC
                    │  (1 replica)    │
                    └─────────────────┘
```

**Services:**
- Frontend → 2 nginx pods (SPA served with compression, caching, security headers)
- Stage-Server → 2 Node.js API servers (WebSocket support, health checks)
- Flask-Backend → 2 Python Flask workers (AI/ML backend)
- PostgreSQL → 1 StatefulSet pod (persistent data, 50Gi storage)
- Redis → 1 StatefulSet pod (session cache, 10Gi storage with AOF)

**Total Resources Requested:**
- CPU: 1.1 cores (requests)
- Memory: 1.5Gi (requests)
- Storage: 60Gi (Postgres + Redis)

---

## Quick Deployment

### 1. Prerequisites
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Ensure connected to cluster
kubectl cluster-info
kubectl get nodes
```

### 2. Push Container Images
```bash
# Build optimized images (from earlier steps)
docker build -t your-registry/atlantiplex-stage:v1.0 -f matrix-studio/web/stage/Dockerfile .
docker build -t your-registry/atlantiplex-flask:v1.0 -f matrix-studio/Dockerfile.python .
docker build -t your-registry/atlantiplex-frontend:v1.0 -f AtlantiplexStudio/Dockerfile .
docker build -t your-registry/atlantiplex-gateway:v1.0 -f gateway/Dockerfile .

# Push to registry
docker push your-registry/atlantiplex-stage:v1.0
docker push your-registry/atlantiplex-flask:v1.0
docker push your-registry/atlantiplex-frontend:v1.0
docker push your-registry/atlantiplex-gateway:v1.0
```

### 3. Update Manifests
```bash
# Edit k8s/02-secrets.yaml with production values OR:
kubectl create secret generic atlantiplex-secrets \
  --from-literal=DB_PASSWORD="your_db_password" \
  --from-literal=REDIS_PASSWORD="your_redis_password" \
  --from-literal=JWT_SECRET="your_jwt_secret" \
  --from-literal=JWT_REFRESH_SECRET="your_jwt_refresh_secret" \
  --from-literal=STRIPE_SECRET_KEY="sk_live_xxxxx" \
  --from-literal=STRIPE_PUBLISHABLE_KEY="pk_live_xxxxx" \
  --from-literal=STRIPE_WEBHOOK_SECRET="whsec_xxxxx" \
  --from-literal=DATABASE_URL="postgresql://atlantiplex:your_db_password@postgres:5432/atlantiplex" \
  --from-literal=REDIS_URL="redis://:your_redis_password@redis:6379/0" \
  -n atlantiplex --dry-run=client -o yaml | kubectl apply -f -
```

### 4. Deploy
```bash
# One-command deployment:
for file in k8s/01-namespace-configmap.yaml k8s/03-postgres.yaml k8s/04-redis.yaml \
            k8s/05-node-deployments.yaml k8s/06-flask-deployment.yaml k8s/07-frontend-ingress.yaml; do
  kubectl apply -f "$file"
done

# Or use the provided script:
./deploy-k8s.sh staging your-registry latest
```

### 5. Wait and Verify
```bash
# Watch pods come up
kubectl get pods -n atlantiplex -w

# Wait 2-3 minutes for all pods to reach Running state
# Check external IP (watch this until it gets an IP)
kubectl get svc nginx-ingress -n atlantiplex -w

# Once you have an EXTERNAL-IP, point DNS to it:
# atlantiplex.example.com → [EXTERNAL-IP]
# api.atlantiplex.example.com → [EXTERNAL-IP]
```

### 6. Test
```bash
# Get external IP
EXTERNAL_IP=$(kubectl get svc nginx-ingress -n atlantiplex -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test frontend
curl http://$EXTERNAL_IP/health

# Test API
curl http://$EXTERNAL_IP/api/health

# View logs
kubectl logs -f deployment/stage-server -n atlantiplex
kubectl logs -f deployment/flask-backend -n atlantiplex
```

---

## Key Features Included

✅ **High Availability**
- Multi-replica deployments (2+ replicas per service)
- Pod anti-affinity (replicas spread across nodes)
- StatefulSets for databases

✅ **Security**
- Non-root containers (UID 1001 for apps, 101 for nginx, 999 for databases)
- Read-only root filesystems where possible
- Dropped capabilities (only NET_BIND_SERVICE added back)
- TLS/HTTPS with nginx
- Security headers (HSTS, CSP, X-Frame-Options, etc.)

✅ **Resource Management**
- CPU/memory requests and limits
- Health checks (liveness + readiness)
- PersistentVolumeClaims for data
- EmptyDir volumes for logs/temp

✅ **Production Ready**
- Secrets management (Kubernetes-native)
- ConfigMap for non-sensitive configuration
- Rolling updates (0 downtime deployments)
- Graceful shutdown with dumb-init

---

## Configuration Files

| File | Purpose | Update? |
|------|---------|---------|
| 01-namespace-configmap.yaml | Namespace + non-sensitive config | CORS_ORIGIN, API_URL |
| 02-secrets.yaml | Database, API keys, TLS | **YES — all values** |
| 03-postgres.yaml | Database | Storage size (if needed) |
| 04-redis.yaml | Cache | Storage size (if needed) |
| 05-node-deployments.yaml | API servers | Image tags, replicas |
| 06-flask-deployment.yaml | Python backend | Image tags, replicas |
| 07-frontend-ingress.yaml | Frontend + LB | Image tags, replicas |
| 08-ingress-nginx.yaml | Alt. Ingress | Only if using nginx-ingress |

---

## Common Operations

```bash
# Scale up stage-server to 5 replicas
kubectl scale deployment stage-server --replicas=5 -n atlantiplex

# Update container image
kubectl set image deployment/stage-server \
  stage-server=your-registry/atlantiplex-stage:v2 -n atlantiplex

# View logs from all stage-server pods
kubectl logs -f deployment/stage-server -n atlantiplex --all-containers

# Port forward postgres to local machine
kubectl port-forward svc/postgres 5432:5432 -n atlantiplex

# Execute migration in pod
kubectl exec deployment/stage-server -n atlantiplex -- npm run migrate

# Get into a pod's shell
kubectl exec -it pod/stage-server-xxxxx -n atlantiplex -- sh

# Check resource usage
kubectl top pods -n atlantiplex
kubectl top nodes

# Delete a deployment (keeps namespace)
kubectl delete deployment stage-server -n atlantiplex

# Delete entire namespace (removes all resources)
kubectl delete namespace atlantiplex
```

---

## Monitoring & Observability

### Built-in Health Checks
- Frontend: `GET /health` returns 200
- Stage-Server: `GET /health` returns 200
- Flask-Backend: `GET /api/health` returns 200
- PostgreSQL: `pg_isready` check
- Redis: `redis-cli ping` check

### View Events
```bash
kubectl get events -n atlantiplex --sort-by='.lastTimestamp'
```

### Resource Metrics
```bash
# Install metrics-server if not present
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Then use:
kubectl top nodes
kubectl top pods -n atlantiplex
```

### Prometheus + Grafana (Optional)
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n atlantiplex
```

---

## Troubleshooting

**"Pod stuck in Pending"**
```bash
kubectl describe pod <pod-name> -n atlantiplex
# Check: PVC binding, storage class, resource requests > available
```

**"CrashLoopBackOff"**
```bash
kubectl logs --previous pod/<pod-name> -n atlantiplex
# Check: Application startup logs, environment variables
```

**"Pods can't connect to database"**
```bash
# Verify DNS resolution
kubectl exec pod/stage-server-xxxxx -n atlantiplex -- nslookup postgres

# Verify connection
kubectl exec pod/postgres-0 -n atlantiplex -- psql -U atlantiplex -d atlantiplex -c "SELECT 1"
```

**"LoadBalancer stuck in Pending"**
```bash
kubectl describe svc nginx-ingress -n atlantiplex
# For local k8s (Docker Desktop, Minikube), use NodePort instead:
kubectl patch svc nginx-ingress -p '{"spec": {"type": "NodePort"}}' -n atlantiplex
```

---

## Storage Requirements

| Service | Type | Size | Mount Point | Notes |
|---------|------|------|-------------|-------|
| PostgreSQL | PVC | 50Gi | /var/lib/postgresql/data | Persistent, survives pod restart |
| Redis | PVC | 10Gi | /data | AOF persistence enabled |
| Stage-Server | emptyDir | Varies | /app/logs, /app/uploads | Lost on pod restart |
| Flask | emptyDir | Varies | /app/logs, /app/core/recordings | Lost on pod restart |

---

## Next Steps

1. ✅ Read `k8s/DEPLOYMENT_GUIDE.md` for detailed instructions
2. ✅ Update `k8s/02-secrets.yaml` with production values
3. ✅ Update image tags in deployment manifests to match your registry
4. ✅ Run deployment script or manually apply manifests
5. ✅ Wait for all pods to reach Running status
6. ✅ Configure DNS to point to LoadBalancer IP
7. ✅ Set up monitoring (Prometheus, Datadog, New Relic, etc.)
8. ✅ Configure log aggregation (ELK, Splunk, CloudLogging, etc.)
9. ✅ Set up backups for PostgreSQL
10. ✅ Test failover and recovery procedures

---

## Reference URLs

- Kubernetes Docs: https://kubernetes.io/docs/
- kubectl Cheat Sheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- StatefulSets: https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/
- Services: https://kubernetes.io/docs/concepts/services-networking/service/
- Ingress: https://kubernetes.io/docs/concepts/services-networking/ingress/
- PersistentVolumes: https://kubernetes.io/docs/concepts/storage/persistent-volumes/
- ConfigMaps & Secrets: https://kubernetes.io/docs/concepts/configuration/

---

**Status:** ✅ Production-ready Kubernetes manifests generated
**Manifest Count:** 8 YAML files + 3 documentation files
**Total Size:** ~50 KB of configuration
**Last Updated:** 2024

All files are in `./k8s/` directory. Ready to deploy!
