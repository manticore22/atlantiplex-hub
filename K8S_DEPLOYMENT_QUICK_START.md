# Kubernetes Deployment - Quick Start

## Overview

Atlantiplex Studio is now deployable to Kubernetes with production-ready manifests.

**Directory:** `./k8s-optimized/`

## Architecture

```
┌─────────────────────────────────────────────┐
│          Ingress (nginx)                    │
│  - atlantiplex.example.com                  │
│  - api.atlantiplex.example.com              │
│  - stage.atlantiplex.example.com            │
└──────────┬──────────────────────────────────┘
           │
    ┌──────┴──────┬──────────┬──────────┐
    │             │          │          │
┌───▼────┐  ┌────▼──┐ ┌────▼──┐ ┌────▼────┐
│Frontend│  │Flask  │ │ Stage │ │Database │
│(nginx) │  │Backend│ │Server │ │(Postgres)
│ x2 pods│  │ x2 pod│ │ x2pod │ │ x1 pod  │
└────────┘  └───────┘ └───────┘ └─────────┘
                                   │
                            ┌──────┴──────┐
                            │ Redis Cache │
                            │   x1 pod    │
                            └─────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `00-namespace-config.yaml` | Namespace, ConfigMap, Secrets, StorageClass |
| `01-postgres.yaml` | PostgreSQL StatefulSet + Service |
| `02-redis.yaml` | Redis StatefulSet + Service |
| `03-flask-backend.yaml` | Flask Deployment + HPA |
| `04-stage-server.yaml` | Stage Server Deployment + HPA |
| `05-frontend.yaml` | Frontend Nginx Deployment + HPA |
| `06-ingress-networking.yaml` | Ingress + NetworkPolicy |
| `07-rbac-policies.yaml` | Pod Disruption Budgets + Resource Limits |
| `deploy.sh` | Automated deployment script |
| `README.md` | Detailed documentation |

## Quick Start

### Option 1: Automated Deployment (Recommended)

```bash
cd k8s-optimized
./deploy.sh
```

The script will:
- Check prerequisites (kubectl, cluster access)
- Prompt for configuration (registry, domain)
- Deploy all manifests in correct order
- Wait for services to be ready
- Print deployment summary

### Option 2: Manual Deployment

```bash
# Set variables
export DOCKER_REGISTRY=docker.io/your-username
export DOMAIN=your-domain.com

# Apply manifests
kubectl apply -f k8s-optimized/00-namespace-config.yaml
kubectl apply -f k8s-optimized/01-postgres.yaml
kubectl apply -f k8s-optimized/02-redis.yaml

# Wait for databases
kubectl wait --for=condition=ready pod -l app=postgres -n atlantiplex --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n atlantiplex --timeout=300s

# Apply applications
kubectl apply -f k8s-optimized/03-flask-backend.yaml
kubectl apply -f k8s-optimized/04-stage-server.yaml
kubectl apply -f k8s-optimized/05-frontend.yaml

# Apply networking
kubectl apply -f k8s-optimized/06-ingress-networking.yaml
kubectl apply -f k8s-optimized/07-rbac-policies.yaml
```

## Before Deployment

### 1. Update Secrets

Edit `00-namespace-config.yaml` and replace:
- `DB_PASSWORD` — database password
- `REDIS_PASSWORD` — redis password
- `JWT_SECRET` — JWT secret key
- `JWT_REFRESH_SECRET` — JWT refresh secret
- `STRIPE_SECRET_KEY` — Stripe secret key
- `STRIPE_PUBLISHABLE_KEY` — Stripe public key
- `STRIPE_WEBHOOK_SECRET` — Webhook secret
- `CORS_ORIGIN` — your domain

### 2. Update Docker Registry

Replace `DOCKER_REGISTRY` in:
- `03-flask-backend.yaml`
- `04-stage-server.yaml`
- `05-frontend.yaml`

Example:
```bash
sed -i 's/DOCKER_REGISTRY/myregistry.azurecr.io/g' k8s-optimized/*.yaml
```

### 3. Update Domain

Replace `atlantiplex.example.com` in `06-ingress-networking.yaml`:
```bash
sed -i 's/atlantiplex.example.com/your-domain.com/g' k8s-optimized/06-ingress-networking.yaml
```

## Verification

### Check Deployment Status

```bash
# All resources
kubectl get all -n atlantiplex

# Specific pods
kubectl get pods -n atlantiplex

# Services
kubectl get svc -n atlantiplex

# Ingress
kubectl get ingress -n atlantiplex

# HPA status
kubectl get hpa -n atlantiplex
```

### View Logs

```bash
# Flask backend
kubectl logs -n atlantiplex -l app=flask-backend -f

# Stage server
kubectl logs -n atlantiplex -l app=stage-server -f

# Frontend
kubectl logs -n atlantiplex -l app=frontend -f
```

### Test Connectivity

```bash
# Port forward to frontend
kubectl port-forward -n atlantiplex svc/frontend 8080:80

# Visit http://localhost:8080 in browser
```

## Scaling

### Manual Scale

```bash
# Scale to 3 replicas
kubectl scale deployment flask-backend --replicas=3 -n atlantiplex
kubectl scale deployment stage-server --replicas=3 -n atlantiplex
kubectl scale deployment frontend --replicas=4 -n atlantiplex
```

### Auto Scale (HPA)

Already configured with:
- Min: 2 replicas
- Max: 5 replicas
- CPU threshold: 70%
- Memory threshold: 80%

Monitor:
```bash
kubectl get hpa -n atlantiplex -w
```

## Database Operations

### Backup PostgreSQL

```bash
kubectl exec -n atlantiplex postgres-0 -- \
  pg_dump -U atlantiplex atlantiplex > backup.sql
```

### Restore PostgreSQL

```bash
kubectl exec -i -n atlantiplex postgres-0 -- \
  psql -U atlantiplex atlantiplex < backup.sql
```

### Access PostgreSQL Pod

```bash
kubectl exec -it -n atlantiplex postgres-0 -- \
  psql -U atlantiplex -d atlantiplex
```

## Cleanup

```bash
# Delete entire namespace
kubectl delete namespace atlantiplex

# Delete specific resource
kubectl delete deployment flask-backend -n atlantiplex
kubectl delete statefulset postgres -n atlantiplex
```

## Troubleshooting

### Pod CrashLoopBackOff

```bash
# Check logs
kubectl logs -n atlantiplex POD_NAME

# Check events
kubectl describe pod -n atlantiplex POD_NAME
```

Common issues:
- Missing secrets (check POSTGRES_PASSWORD)
- Image pull errors (verify registry credentials)
- Database connection failure (check DATABASE_URL)

### Pending Pods

```bash
# Check resource availability
kubectl top nodes

# Check PVC status
kubectl get pvc -n atlantiplex

# Check storage classes
kubectl get storageclass
```

### Service Unreachable

```bash
# Check endpoints
kubectl get endpoints -n atlantiplex

# Check network policies
kubectl get networkpolicies -n atlantiplex

# Check ingress
kubectl describe ingress -n atlantiplex atlantiplex-ingress
```

## Production Checklist

- [ ] All secrets updated with real values
- [ ] Docker registry configured with credentials
- [ ] Domain names configured correctly
- [ ] TLS certificates issued (via cert-manager)
- [ ] Database backups configured
- [ ] Monitoring and alerting set up
- [ ] Resource limits appropriate for cluster
- [ ] Network policies tested
- [ ] Pod disruption budgets verified
- [ ] Load testing completed
- [ ] Disaster recovery plan documented

## Advanced Configuration

### Change Replica Count

Edit `03-flask-backend.yaml`, `04-stage-server.yaml`, `05-frontend.yaml`:
```yaml
spec:
  replicas: 3  # Change this value
```

### Update Resource Limits

Edit deployment specs:
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

### Configure Ingress Class

Update in `06-ingress-networking.yaml` if using different ingress controller:
```yaml
annotations:
  kubernetes.io/ingress.class: nginx  # Change to your controller
```

## Support

For detailed information, see `README.md` in this directory.

For issues:
1. Check pod logs: `kubectl logs -n atlantiplex POD_NAME`
2. Check pod events: `kubectl describe pod -n atlantiplex POD_NAME`
3. Check node resources: `kubectl top nodes`
4. Review ingress: `kubectl describe ingress -n atlantiplex atlantiplex-ingress`

---

**Updated:** February 2025  
**Version:** 1.0  
**Maintainer:** Atlantiplex Team
