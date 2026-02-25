# Kubernetes Deployment Guide

This directory contains production-ready Kubernetes manifests for deploying Atlantiplex Studio.

## Prerequisites

- Kubernetes cluster (v1.24+)
- kubectl configured with cluster access
- Docker images pushed to a Docker registry (Docker Hub, ECR, GCR, etc.)
- StorageClass configured (optional, uses gp3 by default)
- Ingress controller (nginx-ingress recommended)
- cert-manager (for TLS certificates)

## Directory Structure

```
k8s-optimized/
├── 00-namespace-config.yaml      # Namespace, ConfigMap, Secrets, StorageClass
├── 01-postgres.yaml              # PostgreSQL StatefulSet + Service
├── 02-redis.yaml                 # Redis StatefulSet + Service
├── 03-flask-backend.yaml         # Flask Deployment + Service + HPA
├── 04-stage-server.yaml          # Stage Server Deployment + Service + HPA
├── 05-frontend.yaml              # Frontend Nginx Deployment + Service + HPA
├── 06-ingress-networking.yaml    # Ingress + NetworkPolicy
├── 07-rbac-policies.yaml         # PDB, ResourceQuota, LimitRange
└── README.md                      # This file
```

## Quick Start

### 1. Update Configuration Files

Before deploying, update sensitive values:

```bash
# Edit secrets (replace with actual values)
kubectl create secret generic atlantiplex-secrets \
  --from-literal=DB_USER=atlantiplex \
  --from-literal=DB_PASSWORD=YOUR_STRONG_PASSWORD \
  --from-literal=REDIS_PASSWORD=YOUR_REDIS_PASSWORD \
  --from-literal=JWT_SECRET=YOUR_JWT_SECRET \
  --from-literal=JWT_REFRESH_SECRET=YOUR_JWT_REFRESH \
  --from-literal=STRIPE_SECRET_KEY=YOUR_STRIPE_SECRET \
  --from-literal=STRIPE_PUBLISHABLE_KEY=YOUR_STRIPE_PUBLIC \
  --from-literal=STRIPE_WEBHOOK_SECRET=YOUR_WEBHOOK_SECRET \
  --from-literal=CORS_ORIGIN=https://atlantiplex.example.com \
  -n atlantiplex --dry-run=client -o yaml > k8s-optimized/00-namespace-config.yaml.secrets
```

Or manually edit `00-namespace-config.yaml` and replace all `REPLACE_WITH_*` values.

### 2. Update Docker Registry

Replace `DOCKER_REGISTRY` in:
- `03-flask-backend.yaml`
- `04-stage-server.yaml`
- `05-frontend.yaml`

Example for Docker Hub:
```bash
sed -i 's/DOCKER_REGISTRY/myusername/g' *.yaml
```

Example for AWS ECR:
```bash
sed -i 's|DOCKER_REGISTRY|123456789.dkr.ecr.us-east-1.amazonaws.com|g' *.yaml
```

### 3. Update Ingress Domains

Replace `atlantiplex.example.com` in `06-ingress-networking.yaml`:
```bash
sed -i 's/atlantiplex.example.com/your-domain.com/g' k8s-optimized/06-ingress-networking.yaml
```

### 4. Deploy to Kubernetes

Deploy in order:

```bash
# Create namespace and config
kubectl apply -f k8s-optimized/00-namespace-config.yaml

# Deploy databases
kubectl apply -f k8s-optimized/01-postgres.yaml
kubectl apply -f k8s-optimized/02-redis.yaml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n atlantiplex --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n atlantiplex --timeout=300s

# Deploy applications
kubectl apply -f k8s-optimized/03-flask-backend.yaml
kubectl apply -f k8s-optimized/04-stage-server.yaml
kubectl apply -f k8s-optimized/05-frontend.yaml

# Deploy ingress and networking
kubectl apply -f k8s-optimized/06-ingress-networking.yaml
kubectl apply -f k8s-optimized/07-rbac-policies.yaml

# Or deploy all at once:
kubectl apply -f k8s-optimized/
```

### 5. Verify Deployment

```bash
# Check namespace
kubectl get ns

# Check all resources
kubectl get all -n atlantiplex

# Check pod status
kubectl get pods -n atlantiplex

# Check services
kubectl get svc -n atlantiplex

# Check ingress
kubectl get ingress -n atlantiplex

# Check HPA status
kubectl get hpa -n atlantiplex
```

### 6. View Logs

```bash
# Flask backend
kubectl logs -n atlantiplex -l app=flask-backend -f

# Stage server
kubectl logs -n atlantiplex -l app=stage-server -f

# Frontend
kubectl logs -n atlantiplex -l app=frontend -f

# PostgreSQL
kubectl logs -n atlantiplex -l app=postgres -f

# Redis
kubectl logs -n atlantiplex -l app=redis -f
```

### 7. Port Forward for Testing

```bash
# Frontend (http://localhost:8080)
kubectl port-forward -n atlantiplex svc/frontend 8080:80

# Flask API (http://localhost:5000)
kubectl port-forward -n atlantiplex svc/flask-backend 5000:5000

# Stage Server (http://localhost:9001)
kubectl port-forward -n atlantiplex svc/stage-server 9001:9001
```

## Scaling

### Manual Scaling

```bash
# Scale Flask backend
kubectl scale deployment flask-backend --replicas=3 -n atlantiplex

# Scale Stage server
kubectl scale deployment stage-server --replicas=3 -n atlantiplex

# Scale Frontend
kubectl scale deployment frontend --replicas=4 -n atlantiplex
```

### Auto Scaling (HPA)

Horizontal Pod Autoscaler is configured in each deployment:
- **Min replicas:** 2
- **Max replicas:** 5
- **CPU threshold:** 70%
- **Memory threshold:** 80%

Monitor HPA status:
```bash
kubectl get hpa -n atlantiplex -w
```

## Persistence & Storage

### Database Persistence

PostgreSQL and Redis use `StatefulSet` with persistent volumes:

```bash
# View persistent volumes
kubectl get pv

# View persistent volume claims
kubectl get pvc -n atlantiplex

# Backup PostgreSQL
kubectl exec -n atlantiplex postgres-0 -- \
  pg_dump -U atlantiplex atlantiplex > backup.sql

# Restore PostgreSQL
kubectl exec -i -n atlantiplex postgres-0 -- \
  psql -U atlantiplex atlantiplex < backup.sql
```

## Security

### Network Policy

- All traffic restricted to atlantiplex namespace
- Only ingress-nginx can access frontend
- Internal DNS (port 53) allowed for service discovery
- External HTTPS (port 443) allowed for outbound connections

### Pod Security

- All containers run as non-root users
- Read-only root filesystem where possible (frontend)
- Capabilities dropped (except NET_BIND_SERVICE for nginx)
- Security contexts enforced

### Secrets Management

- Use Kubernetes Secrets for sensitive data
- Consider using external secret managers (Sealed Secrets, Vault)
- Never commit secrets to Git

## Monitoring & Logging

### Recommended Additions

```bash
# Install Prometheus for metrics
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n atlantiplex

# Install ELK for logging
helm repo add elastic https://helm.elastic.co
helm install elasticsearch elastic/elasticsearch -n atlantiplex

# Install cert-manager for TLS
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager -n cert-manager
```

## Debugging

### Check pod events
```bash
kubectl describe pod POD_NAME -n atlantiplex
```

### Debug pod
```bash
kubectl debug pod POD_NAME -n atlantiplex -it --image=alpine:latest
```

### Check resource usage
```bash
kubectl top nodes
kubectl top pods -n atlantiplex
```

### Check ingress status
```bash
kubectl describe ingress atlantiplex-ingress -n atlantiplex
```

## Cleanup

```bash
# Delete all resources in namespace
kubectl delete namespace atlantiplex

# Delete specific resource
kubectl delete deployment flask-backend -n atlantiplex
```

## Production Checklist

- [ ] All secrets updated with actual values
- [ ] Docker registry credentials configured
- [ ] Ingress domains configured correctly
- [ ] SSL/TLS certificates issued
- [ ] Database backups configured
- [ ] Monitoring and alerting set up
- [ ] Resource limits appropriate for your cluster
- [ ] Network policies tested
- [ ] Pod disruption budgets verified
- [ ] High availability replicas set (min 2)
- [ ] Load testing completed
- [ ] Disaster recovery plan in place

## Troubleshooting

### CrashLoopBackOff

Check pod logs and events:
```bash
kubectl logs POD_NAME -n atlantiplex
kubectl describe pod POD_NAME -n atlantiplex
```

Common causes:
- Database connection failure (check DATABASE_URL)
- Missing secrets (check POSTGRES_PASSWORD, etc.)
- Image pull errors (check Docker registry credentials)
- Application startup issues (check app logs)

### Pending Pods

Usually due to:
- Insufficient resources (check node capacity)
- PVC binding issues (check StorageClass)

```bash
kubectl describe pvc PVC_NAME -n atlantiplex
kubectl top nodes
```

### Service Unreachable

Check:
```bash
kubectl get endpoints -n atlantiplex
kubectl get svc -n atlantiplex
kubectl get networkpolicies -n atlantiplex
```

## Advanced Customization

### Update Strategy

Change in deployments for faster rollouts:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 2        # Default: 1
    maxUnavailable: 1  # Default: 0 (safe)
```

### Resource Limits

Adjust CPU/memory in deployment specs:
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

### Affinity Rules

Current config prefers pods on different nodes. For co-location:
```yaml
affinity:
  podAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchLabels:
            app: stage-server
        topologyKey: kubernetes.io/hostname
```

---

## Support

For issues or questions:
1. Check pod logs: `kubectl logs -n atlantiplex POD_NAME`
2. Check pod events: `kubectl describe pod -n atlantiplex POD_NAME`
3. Review deployment manifest: `kubectl get deployment -n atlantiplex -o yaml DEPLOYMENT_NAME`
4. Check resource availability: `kubectl top nodes`

For updates, refer to the main repository and pull latest manifests.
