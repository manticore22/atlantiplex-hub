# Docker Deployment Checklist

## Pre-Deployment

### Environment Setup
- [ ] `.env` file created from `.env.example`
- [ ] All required variables configured (DB_PASSWORD, REDIS_PASSWORD, JWT_SECRET, Stripe keys)
- [ ] Production passwords are strong (minimum 32 characters, mixed case/numbers/symbols)
- [ ] API URLs point to correct domain
- [ ] CORS_ORIGIN matches frontend domain
- [ ] No secrets committed to git (check .gitignore includes .env)

### Images Built
- [ ] `docker compose build` completed successfully
- [ ] All 3 images built (stage, flask, frontend)
- [ ] No build warnings or errors
- [ ] Image sizes reasonable (stage ~48MB, flask ~180MB, frontend ~40MB)

### Security Review
- [ ] All services run as non-root users
- [ ] Capabilities dropped (CAP_DROP: ALL)
- [ ] no-new-privileges set on all services
- [ ] Health checks configured
- [ ] .dockerignore excludes sensitive files
- [ ] Secrets not hardcoded in Dockerfiles

### Testing
- [ ] Health checks pass: `make health`
- [ ] Services respond to requests
- [ ] Database migrations run: `docker compose exec flask-backend flask db upgrade`
- [ ] Frontend loads without errors
- [ ] API endpoints accessible

## Development Deployment

### Quick Start
- [ ] `.env` created
- [ ] `docker compose -f docker-compose.dev.yml up -d` runs successfully
- [ ] All services healthy: `docker compose ps`
- [ ] Frontend loads at http://localhost:5173
- [ ] APIs respond at http://localhost:9001 and http://localhost:5000
- [ ] Hot reload works (edit file, changes appear immediately)
- [ ] Logs accessible: `docker compose logs -f`

## Production Deployment (Single Host)

### Pre-Flight
- [ ] `.env.production` created with production values
- [ ] Firewall allows ports 80, 443
- [ ] SSL certificates in place (if using HTTPS)
- [ ] Database backups configured
- [ ] Logs directed to centralized logging (optional)
- [ ] Resource limits appropriate for host

### Deployment
- [ ] `docker compose -f docker-compose.prod.yml --env-file .env.production up -d`
- [ ] All services start successfully
- [ ] Service health checks pass within 90 seconds
- [ ] `docker compose ps` shows all running

### Post-Deployment Verification
- [ ] Application accessible at configured domain
- [ ] Frontend loads without errors
- [ ] API requests return expected responses
- [ ] Database operations functional
- [ ] Redis cache working
- [ ] Logs clean (no ERROR level messages)
- [ ] Performance acceptable (monitor CPU/memory)

### Monitoring
- [ ] Resource usage normal: `docker stats`
- [ ] No container restarts: `docker compose ps`
- [ ] Logs checked for errors: `docker compose logs`
- [ ] Health checks passing: all containers show "healthy"

## Production Deployment (Docker Swarm)

### Pre-Flight
- [ ] Docker Swarm initialized: `docker swarm init`
- [ ] All manager nodes connected
- [ ] Storage backend configured (for volumes)
- [ ] Secrets manager configured
- [ ] Load balancer configured (optional)

### Deployment
- [ ] Secrets created: `docker secret create db_password <value>`
- [ ] `docker stack deploy -c docker-compose.prod.yml atlantiplex`
- [ ] Services replicated as configured
- [ ] Service health checks green: `docker service ls`

### Post-Deployment
- [ ] `docker service logs atlantiplex_stage-server` shows no errors
- [ ] `docker service logs atlantiplex_flask-backend` shows no errors
- [ ] `docker service logs atlantiplex_postgres` shows no errors
- [ ] Load balancing working (requests distributed across replicas)
- [ ] Failover tested (restart a replica, check automatic recovery)

## Kubernetes Deployment

### Pre-Flight
- [ ] Cluster accessible: `kubectl cluster-info`
- [ ] Images pushed to registry: `docker push my-registry/atlantiplex-stage:latest`
- [ ] Registry credentials configured
- [ ] Persistent volumes available
- [ ] Ingress controller installed

### Deployment
- [ ] Manifests created (Deployment, Service, ConfigMap, Secret, PersistentVolume)
- [ ] `kubectl apply -f manifests/` successful
- [ ] Pods running: `kubectl get pods`
- [ ] Services exposed: `kubectl get svc`
- [ ] Ingress configured

### Post-Deployment
- [ ] `kubectl describe pod <pod-name>` shows no errors
- [ ] `kubectl logs <pod-name>` shows normal operation
- [ ] Application accessible through ingress domain
- [ ] Pods restarted on failure (tested by killing pod)

## Ongoing Operations

### Daily
- [ ] Check service status: `docker compose ps`
- [ ] Review logs for errors: `docker compose logs --tail=100`
- [ ] Monitor resource usage: `docker stats`

### Weekly
- [ ] Backup database: `docker compose exec postgres pg_dump ... > backup.sql`
- [ ] Verify backups valid
- [ ] Update base images if available
- [ ] Review security advisories

### Monthly
- [ ] Security scan images: `docker scout cves atlantiplex-stage`
- [ ] Review access logs for anomalies
- [ ] Test failover/recovery procedures
- [ ] Update documentation if needed

## Scaling Checklist

### Horizontal Scaling (Multiple Replicas)
- [ ] Nginx upstreams configured for multiple backends
- [ ] Load balancing strategy selected
- [ ] Health checks passing on all replicas
- [ ] Database connection pooling configured
- [ ] Redis replication configured (if needed)
- [ ] Session persistence working

### Vertical Scaling (More Resources)
- [ ] Resource limits adjusted in compose file
- [ ] NODE_OPTIONS updated for larger heaps
- [ ] Database tuned for increased load
- [ ] Nginx worker processes adjusted

## Troubleshooting Checklist

### Services Won't Start
- [ ] `docker compose logs <service>` - check error messages
- [ ] Environment variables correct: `docker compose config`
- [ ] Ports not in use: `lsof -i :5173`
- [ ] Disk space available: `docker system df`

### Database Connection Fails
- [ ] PostgreSQL running and healthy: `docker compose ps`
- [ ] DATABASE_URL correct: `docker compose exec app env | grep DATABASE_URL`
- [ ] Database exists: `docker compose exec postgres psql -l`
- [ ] Firewall allows connection

### High Memory Usage
- [ ] Check memory stats: `docker stats`
- [ ] Reduce NODE_OPTIONS --max-old-space-size
- [ ] Check for memory leaks in logs
- [ ] Increase available memory or reduce replicas

### SSL/TLS Issues
- [ ] Certificates present in nginx/ssl directory
- [ ] Certificate paths correct in nginx.conf
- [ ] Certificates not expired: `openssl x509 -in cert.pem -noout -dates`
- [ ] Nginx logs show certificate errors: `docker compose logs nginx`

## Performance Optimization

### Build Performance
- [ ] `.dockerignore` properly configured
- [ ] Layer caching not invalidated unnecessarily
- [ ] Multi-stage builds used
- [ ] Build time < 5 minutes for initial build

### Runtime Performance
- [ ] Gzip compression enabled in Nginx
- [ ] Static asset caching headers configured
- [ ] Database indexes created
- [ ] Redis caching implemented
- [ ] Connection pooling configured

### Memory Usage
- [ ] NODE_OPTIONS appropriate for workload
- [ ] Python garbage collection tuned
- [ ] Memory limits set in resource limits
- [ ] OOM killer not triggered: `docker inspect <container> | grep OOMKilled`

## Security Hardening

### Container Security
- [ ] All processes run as non-root
- [ ] Capabilities dropped (CAP_DROP: ALL)
- [ ] Read-only root filesystem where possible
- [ ] Health checks prevent hung containers
- [ ] No interactive shells in production

### Network Security
- [ ] Services only expose necessary ports
- [ ] Internal network used for service-to-service communication
- [ ] Firewall rules restrict access
- [ ] HTTPS/TLS enabled for external communication

### Secret Management
- [ ] Secrets not in environment variables (use Docker Secrets in Swarm)
- [ ] Secrets rotated regularly
- [ ] Access logs audited for suspicious activity

### Compliance
- [ ] Data encryption at rest (if required)
- [ ] Data encryption in transit (HTTPS)
- [ ] Access logs maintained
- [ ] Audit trail configured

## Disaster Recovery

### Backup Strategy
- [ ] Database backed up daily
- [ ] Backup retention policy defined (e.g., 30 days)
- [ ] Backup verification automated
- [ ] Off-site backup storage configured

### Recovery Testing
- [ ] Restore from backup tested monthly
- [ ] RTO (Recovery Time Objective) measured
- [ ] RPO (Recovery Point Objective) defined
- [ ] Runbook documented and tested

### High Availability
- [ ] Multiple replicas configured
- [ ] Load balancer configured
- [ ] Health checks detect failures
- [ ] Automatic failover working

## Documentation

### Setup Documentation
- [ ] README.md updated with Docker setup
- [ ] CONTAINERIZATION_GUIDE.md reviewed
- [ ] DOCKER_QUICK_REFERENCE.md accessible to team
- [ ] Architecture diagram created (optional)

### Runbooks
- [ ] Deployment procedure documented
- [ ] Scaling procedure documented
- [ ] Disaster recovery procedure documented
- [ ] Troubleshooting guide available

### Code Documentation
- [ ] Dockerfile comments explain each section
- [ ] docker-compose.yml services documented
- [ ] Environment variables documented with defaults

## Team Training

- [ ] Team trained on Docker basics
- [ ] Team trained on this specific setup
- [ ] Team can deploy using provided commands
- [ ] Team understands troubleshooting steps
- [ ] On-call rotation established with knowledge

## Sign-Off

- [ ] Development deployment tested: ________________ Date: _______
- [ ] Production deployment tested: ________________ Date: _______
- [ ] Security review completed: ________________ Date: _______
- [ ] Performance tested: ________________ Date: _______
- [ ] Team trained: ________________ Date: _______
- [ ] Documentation complete: ________________ Date: _______
- [ ] Go-live approved: ________________ Date: _______

---

For detailed information, refer to:
- CONTAINERIZATION_GUIDE.md - Full deployment guide
- DOCKER_QUICK_REFERENCE.md - Quick commands
- CONTAINERIZATION_SUMMARY.md - Overview
