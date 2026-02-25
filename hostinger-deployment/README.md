# Hostinger Deployment Guide

## Overview

Complete Docker-based deployment for Atlantiplex Studio on Hostinger VPS hosting.

**Includes:**
- Website (www.atlantiplex.com)
- Studio (studio.atlantiplex.com)
- API (api.atlantiplex.com)
- PostgreSQL Database
- Redis Cache
- Nginx Reverse Proxy with SSL/TLS

## Prerequisites

1. **Hostinger VPS** with Docker and Docker Compose installed
2. **Domain names** registered and DNS configured
3. **SSL certificates** (Let's Encrypt recommended)
4. **SSH access** to your Hostinger VPS

## Quick Start

### 1. SSH into Hostinger VPS

```bash
ssh user@your-hostinger-ip
cd /home/user/atlantiplex
```

### 2. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env
```

Required values to change:
- `DB_PASSWORD` — Strong database password
- `REDIS_PASSWORD` — Strong Redis password
- `JWT_SECRET` — Random JWT secret
- `STRIPE_*` — Your Stripe API keys
- Domain URLs

### 3. Update Domain Names

Edit `nginx/conf.d/website.conf`, `nginx/conf.d/studio.conf`, `nginx/conf.d/api.conf`:

```bash
# Replace atlantiplex.com with your domain
sed -i 's/atlantiplex.com/your-domain.com/g' nginx/conf.d/*.conf
```

### 4. Setup SSL Certificates

Generate certificates using Let's Encrypt:

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Generate certificates (stop nginx first)
docker-compose down

certbot certonly --standalone \
  -d your-domain.com \
  -d www.your-domain.com \
  -d studio.your-domain.com \
  -d api.your-domain.com

# Copy certificates to deployment
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/atlantiplex.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/atlantiplex.key
sudo chown $USER:$USER nginx/ssl/*
```

### 5. Deploy

```bash
bash deploy.sh
```

The script will:
- Build Docker images
- Start all services
- Verify health checks
- Show URLs and useful commands

### 6. Verify Deployment

```bash
# Check services
docker-compose ps

# View logs
docker-compose logs -f

# Test website
curl https://your-domain.com
curl https://studio.your-domain.com
curl https://api.your-domain.com/api/health
```

## Directory Structure

```
hostinger-deployment/
├── docker-compose.yml          # Main deployment config
├── .env.example                # Environment template
├── deploy.sh                   # Deployment script
├── backup.sh                   # Backup script
├── nginx/
│   ├── nginx.conf              # Nginx main config
│   └── conf.d/
│       ├── website.conf        # Website domain
│       ├── studio.conf         # Studio domain
│       └── api.conf            # API domain
└── ssl/
    ├── atlantiplex.crt         # SSL certificate
    └── atlantiplex.key         # SSL private key
```

## Configuration Files

### docker-compose.yml

Main deployment configuration with:
- **nginx** — Reverse proxy and load balancer
- **postgres** — Database server
- **redis** — Cache and session store
- **website** — Static website (Node.js)
- **studio** — Creative studio (Nginx)
- **api** — Flask backend API

### nginx/nginx.conf

Global Nginx configuration:
- HTTP/2 support
- Gzip compression
- Rate limiting
- Security headers
- SSL/TLS settings

### nginx/conf.d/*.conf

Domain-specific routing:
- `website.conf` — www.atlantiplex.com → website service
- `studio.conf` — studio.atlantiplex.com → studio service
- `api.conf` — api.atlantiplex.com → api service

## Managing Services

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f nginx
```

### Stop Services

```bash
docker-compose down
```

### Restart Services

```bash
docker-compose restart
docker-compose restart nginx  # Specific service
```

### View Database

```bash
docker-compose exec postgres psql -U atlantiplex -d atlantiplex
```

### Access Redis

```bash
docker-compose exec redis redis-cli
```

### Rebuild Images

```bash
docker-compose build --no-cache
docker-compose up -d
```

## Backups

### Manual Backup

```bash
bash backup.sh
```

Creates backups in `./backups/`:
- PostgreSQL dump (compressed)
- Redis snapshot (compressed)
- Volume archives

### Automated Backups

Create a cron job:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /home/user/atlantiplex && bash backup.sh
```

### Restore from Backup

```bash
# Restore PostgreSQL
docker-compose exec -T postgres psql -U atlantiplex atlantiplex < backups/postgres_TIMESTAMP.sql.gz

# Restore Redis
docker-compose exec -T redis redis-cli SHUTDOWN
# Copy dump.rdb to redis volume
docker-compose exec -T redis redis-cli
```

## SSL/TLS Certificate Renewal

Let's Encrypt certificates expire after 90 days. Auto-renew with cron:

```bash
# Add to crontab
0 0 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /home/user/atlantiplex/nginx/ssl/atlantiplex.crt && cp /etc/letsencrypt/live/your-domain.com/privkey.pem /home/user/atlantiplex/nginx/ssl/atlantiplex.key && docker-compose -f /home/user/atlantiplex/docker-compose.yml restart nginx
```

Or use Certbot's built-in renewal:

```bash
sudo certbot renew --force-renewal
```

## Monitoring

### CPU and Memory Usage

```bash
docker stats
```

### Port Usage

```bash
netstat -tulpn | grep LISTEN
```

### Disk Space

```bash
df -h
docker system df
```

## Troubleshooting

### Services Won't Start

1. Check logs:
   ```bash
   docker-compose logs
   ```

2. Verify ports aren't in use:
   ```bash
   sudo netstat -tulpn | grep -E ':(80|443|5432|6379)'
   ```

3. Check available disk space:
   ```bash
   df -h
   ```

### SSL Certificate Issues

1. Verify certificate files exist:
   ```bash
   ls -la nginx/ssl/
   ```

2. Check certificate validity:
   ```bash
   openssl x509 -in nginx/ssl/atlantiplex.crt -text -noout
   ```

3. Restart Nginx:
   ```bash
   docker-compose restart nginx
   ```

### Database Connection Error

1. Check PostgreSQL logs:
   ```bash
   docker-compose logs postgres
   ```

2. Verify credentials in .env:
   ```bash
   grep DB_ .env
   ```

3. Restart database:
   ```bash
   docker-compose restart postgres
   ```

### Website Not Loading

1. Check Nginx logs:
   ```bash
   docker-compose logs nginx
   ```

2. Verify domain DNS:
   ```bash
   nslookup your-domain.com
   ```

3. Test connectivity:
   ```bash
   curl -I https://your-domain.com
   ```

## Performance Optimization

### Increase Log Rotation

Edit `docker-compose.yml`:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "5m"      # Change to "1m" for more frequent rotation
    max-file: "3"       # Change to "5" to keep more files
```

### Enable Nginx Caching

Add to `nginx/conf.d/website.conf`:

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=content:10m;

location / {
    proxy_cache content;
    proxy_cache_valid 200 10m;
    add_header X-Cache-Status $upstream_cache_status;
}
```

### Database Performance

Increase PostgreSQL shared_buffers:

```bash
docker-compose exec postgres psql -U atlantiplex -d atlantiplex \
  -c "ALTER SYSTEM SET shared_buffers = 256MB;"
docker-compose restart postgres
```

## Production Checklist

- [ ] SSL certificates installed and valid
- [ ] Database backups automated
- [ ] DNS configured correctly
- [ ] Firewall rules configured
- [ ] Monitoring and alerting set up
- [ ] Error logging configured
- [ ] Rate limiting tested
- [ ] Failover procedures documented
- [ ] Security headers verified
- [ ] CORS configuration correct

## Support

For issues or questions:

1. Check logs: `docker-compose logs -f`
2. Verify configuration: `cat .env`
3. Test connectivity: `curl -I https://your-domain.com`
4. Check Docker resources: `docker stats`

## Cleanup

Remove all containers and volumes:

```bash
docker-compose down -v
```

This will NOT delete backups or configuration files.

---

**Version:** 1.0  
**Last Updated:** February 2025  
**Maintainer:** Atlantiplex Team
