#!/bin/bash
# Atlantiplex Kubernetes Quick Reference Card
# Copy and paste commands as needed

# ======================
# CLUSTER SETUP
# ======================

# Verify cluster connection
kubectl cluster-info
kubectl get nodes
kubectl config current-context

# Switch context
kubectl config use-context <context-name>
kubectl config get-contexts

# ======================
# DEPLOYMENT
# ======================

# Create secrets from CLI (recommended for production)
kubectl create secret generic atlantiplex-secrets \
  --from-literal=DB_PASSWORD="$(openssl rand -base64 32)" \
  --from-literal=REDIS_PASSWORD="$(openssl rand -base64 32)" \
  --from-literal=JWT_SECRET="$(openssl rand -base64 64)" \
  --from-literal=JWT_REFRESH_SECRET="$(openssl rand -base64 64)" \
  --from-literal=STRIPE_SECRET_KEY="sk_live_xxxxx" \
  --from-literal=STRIPE_PUBLISHABLE_KEY="pk_live_xxxxx" \
  --from-literal=STRIPE_WEBHOOK_SECRET="whsec_xxxxx" \
  --from-literal=DATABASE_URL="postgresql://atlantiplex:password@postgres:5432/atlantiplex" \
  --from-literal=REDIS_URL="redis://:password@redis:6379/0" \
  -n atlantiplex --dry-run=client -o yaml | kubectl apply -f -

# Deploy all manifests
kubectl apply -f k8s/01-namespace-configmap.yaml
kubectl apply -f k8s/03-postgres.yaml
kubectl apply -f k8s/04-redis.yaml
kubectl apply -f k8s/05-node-deployments.yaml
kubectl apply -f k8s/06-flask-deployment.yaml
kubectl apply -f k8s/07-frontend-ingress.yaml

# Deploy single file
kubectl apply -f k8s/05-node-deployments.yaml

# ======================
# MONITORING
# ======================

# Watch pod status
kubectl get pods -n atlantiplex -w

# Watch service IPs
kubectl get svc -n atlantiplex -w

# Get all resources
kubectl get all -n atlantiplex

# Get external IP
kubectl get svc nginx-ingress -n atlantiplex

# ======================
# LOGS & DEBUGGING
# ======================

# View logs
kubectl logs -f pod/<pod-name> -n atlantiplex
kubectl logs -f deployment/stage-server -n atlantiplex
kubectl logs -f deployment/flask-backend -n atlantiplex
kubectl logs -f deployment/frontend -n atlantiplex

# View previous logs (for crashed pods)
kubectl logs --previous pod/<pod-name> -n atlantiplex

# View all containers' logs
kubectl logs -f deployment/stage-server -n atlantiplex --all-containers

# Stream logs from all pods in deployment
kubectl logs -f -l app=stage-server -n atlantiplex

# Describe pod
kubectl describe pod <pod-name> -n atlantiplex

# Get events (sorted by time)
kubectl get events -n atlantiplex --sort-by='.lastTimestamp'

# ======================
# SCALING & UPDATES
# ======================

# Scale deployment
kubectl scale deployment stage-server --replicas=5 -n atlantiplex

# Update image
kubectl set image deployment/stage-server \
  stage-server=your-registry/atlantiplex-stage:v2 \
  -n atlantiplex

# Rollout status
kubectl rollout status deployment/stage-server -n atlantiplex

# Rollback to previous version
kubectl rollout undo deployment/stage-server -n atlantiplex

# View rollout history
kubectl rollout history deployment/stage-server -n atlantiplex

# ======================
# POD OPERATIONS
# ======================

# Execute command in pod
kubectl exec pod/<pod-name> -n atlantiplex -- <command>

# Interactive shell
kubectl exec -it pod/<pod-name> -n atlantiplex -- /bin/sh

# Copy file from pod
kubectl cp atlantiplex/<pod-name>:/app/logs/app.log ./app.log

# Copy file to pod
kubectl cp ./backup.sql atlantiplex/<pod-name>:/tmp/backup.sql

# ======================
# PORT FORWARDING
# ======================

# Forward pod port
kubectl port-forward pod/<pod-name> 3000:3000 -n atlantiplex

# Forward service port
kubectl port-forward svc/postgres 5432:5432 -n atlantiplex
kubectl port-forward svc/redis 6379:6379 -n atlantiplex
kubectl port-forward svc/stage-server 9001:9001 -n atlantiplex

# Forward on specific interface
kubectl port-forward svc/postgres 0.0.0.0:5432:5432 -n atlantiplex

# ======================
# RESOURCE USAGE
# ======================

# CPU and memory by pod
kubectl top pods -n atlantiplex

# CPU and memory by node
kubectl top nodes

# Describe node resources
kubectl describe nodes

# Check available storage
kubectl get pvc -n atlantiplex

# ======================
# CONFIGURATION MANAGEMENT
# ======================

# Get secret (base64 encoded)
kubectl get secret atlantiplex-secrets -n atlantiplex -o jsonpath='{.data}'

# Decode secret
kubectl get secret atlantiplex-secrets -n atlantiplex -o jsonpath='{.data.DB_PASSWORD}' | base64 -d

# Edit secret
kubectl edit secret atlantiplex-secrets -n atlantiplex

# Get ConfigMap
kubectl get configmap atlantiplex-config -n atlantiplex -o yaml

# Edit ConfigMap
kubectl edit configmap atlantiplex-config -n atlantiplex

# ======================
# DATABASE OPERATIONS
# ======================

# Connect to postgres
kubectl exec -it pod/postgres-0 -n atlantiplex -- psql -U atlantiplex -d atlantiplex

# Run SQL
kubectl exec pod/postgres-0 -n atlantiplex -- psql -U atlantiplex -d atlantiplex -c "SELECT 1"

# Backup database
kubectl exec pod/postgres-0 -n atlantiplex -- pg_dump -U atlantiplex atlantiplex > backup.sql

# Restore database
cat backup.sql | kubectl exec -i pod/postgres-0 -n atlantiplex -- psql -U atlantiplex atlantiplex

# Connect to redis
kubectl exec -it pod/redis-0 -n atlantiplex -- redis-cli
# Type: AUTH <password>
# Then: PING

# ======================
# TROUBLESHOOTING
# ======================

# Describe pod (detailed info)
kubectl describe pod <pod-name> -n atlantiplex

# Get pod events
kubectl get events -n atlantiplex --field-selector involvedObject.name=<pod-name>

# Check DNS resolution
kubectl exec pod/<pod-name> -n atlantiplex -- nslookup postgres

# Test connectivity
kubectl exec pod/<pod-name> -n atlantiplex -- wget -O- http://stage-server:9001/health

# Run debug pod
kubectl run -it debug --image=alpine --rm -n atlantiplex -- sh

# ======================
# DELETION & CLEANUP
# ======================

# Delete pod (will be recreated)
kubectl delete pod <pod-name> -n atlantiplex

# Delete deployment
kubectl delete deployment stage-server -n atlantiplex

# Delete all in namespace
kubectl delete all -n atlantiplex

# Delete namespace (removes all resources)
kubectl delete namespace atlantiplex

# Delete PVC (keeps data if backed up)
kubectl delete pvc postgres-pvc -n atlantiplex

# ======================
# USEFUL ALIASES
# ======================

# Add these to .bashrc or .zshrc
alias k=kubectl
alias kn="kubectl config set-context --current --namespace"
alias kgp="kubectl get pods -n atlantiplex"
alias klf="kubectl logs -f deployment/stage-server -n atlantiplex"
alias kex="kubectl exec -it"

# Usage:
# k get pods
# kn atlantiplex
# kgp
# klf
# kex pod/stage-server-xxxxx -n atlantiplex -- sh

# ======================
# IMPORTANT ENDPOINTS
# ======================

# Frontend health: http://<external-ip>/health
# API health: http://<external-ip>/api/health
# Flask health: http://<external-ip>/flask/api/health

# Get external IP:
kubectl get svc nginx-ingress -n atlantiplex -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# ======================
# MONITORING
# ======================

# Prometheus (if installed)
kubectl port-forward -n atlantiplex svc/prometheus 9090:9090

# Grafana (if installed)
kubectl port-forward -n atlantiplex svc/grafana 3000:3000

# ======================
# RESOURCE QUOTAS
# ======================

# Create quota
kubectl create quota compute-quota \
  --hard=cpu=10,memory=20Gi,pods=100 \
  -n atlantiplex

# View quota
kubectl describe quota -n atlantiplex

# ======================
# NETWORK POLICIES
# ======================

# Allow all (default)
# Already configured in manifests

# Deny all ingress (if needed)
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

# ======================
# BACKUP & RESTORE
# ======================

# Backup entire namespace
kubectl get all -n atlantiplex -o yaml > atlantiplex-backup.yaml

# Restore from backup
kubectl apply -f atlantiplex-backup.yaml

# Backup single resource
kubectl get deployment stage-server -n atlantiplex -o yaml > stage-server-backup.yaml

# ======================
# USEFUL LINKS
# ======================

# Kubernetes Dashboard (if available)
# kubectl proxy --port=8001
# http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/

# Documentation
# https://kubernetes.io/docs/reference/kubectl/cheatsheet/
# https://kubernetes.io/docs/concepts/workloads/
# https://kubernetes.io/docs/tasks/

echo "✅ Atlantiplex Kubernetes Quick Reference loaded"
