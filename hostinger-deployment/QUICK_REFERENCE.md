# Hostinger Deployment - Quick Reference

## URLs After Deployment

```
Website:  https://www.atlantiplex.com
Studio:   https://studio.atlantiplex.com
API:      https://api.atlantiplex.com/api/health
```

## Quick Commands

```bash
# Deploy
bash deploy.sh

# View status
docker-compose ps

# View logs
docker-compose logs -f

# Stop all
docker-compose down

# Restart services
docker-compose restart

# Backup
bash backup.sh

# Database access
docker-compose exec postgres psql -U atlantiplex

# Redis access
docker-compose exec redis redis-cli
```

## Setup Checklist

- [ ] Edit `.env` with passwords and Stripe keys
- [ ] Update domain names in `nginx/conf.d/*.conf`
- [ ] Generate SSL certificates with Let's Encrypt
- [ ] Copy SSL certs to `nginx/ssl/`
- [ ] Update DNS records to point to Hostinger IP
- [ ] Run `bash deploy.sh`
- [ ] Verify all services are running: `docker-compose ps`
- [ ] Test websites in browser
- [ ] Setup automated backups in crontab
- [ ] Setup certificate renewal in crontab

## File Locations

```
.env                              # Configuration (create from .env.example)
docker-compose.yml                # Services definition
nginx/nginx.conf                  # Nginx main config
nginx/conf.d/website.conf         # Website routing
nginx/conf.d/studio.conf          # Studio routing
nginx/conf.d/api.conf             # API routing
nginx/ssl/atlantiplex.crt         # SSL certificate
nginx/ssl/atlantiplex.key         # SSL private key
backups/                          # Backup files
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Services fail to start | Check `.env` variables, run `docker-compose logs` |
| SSL errors | Verify cert paths, check `openssl x509 -in nginx/ssl/*.crt -text -noout` |
| Connection refused | Check ports: `sudo netstat -tulpn` |
| Database won't connect | Verify `DB_PASSWORD` in `.env`, check PostgreSQL logs |
| Website not loading | Check DNS, verify nginx config, restart nginx |

## Credentials

All default credentials are in `.env`:
- Database: `atlantiplex` user (change password in .env)
- Redis: Protected with password (set in .env)
- API: Protected with JWT (keys in .env)

## Support

Detailed documentation: `README.md`
Deployment script with confirmations: `deploy.sh`
Automated backups: `backup.sh`

## Next Steps

1. **SSH into Hostinger VPS**
   ```bash
   ssh user@your-ip
   cd /path/to/atlantiplex
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your values
   ```

3. **Setup Domains**
   ```bash
   sed -i 's/atlantiplex.com/your-domain.com/g' nginx/conf.d/*.conf
   ```

4. **Generate SSL**
   ```bash
   certbot certonly --standalone -d your-domain.com -d www.your-domain.com ...
   cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/atlantiplex.crt
   cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/atlantiplex.key
   ```

5. **Deploy**
   ```bash
   bash deploy.sh
   ```

6. **Monitor**
   ```bash
   docker-compose logs -f
   ```

---

All services will be running at: `https://your-domain.com`
