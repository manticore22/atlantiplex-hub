Hostinger One-Domain Deployment Guide (Gateway root, Atlantiplex at /atlantiplex)

1) Prepare server
- Ubuntu 22.04 LTS, root access via SSH
- Install Nginx, PostgreSQL, Node, and PM2 (see setup.sh in this bundle)

2) Deploy patch bundle
- Upload Seraphinix_Bundle.zip or the contents patch to /opt/seraphinix
- Unzip and place:
  - gateway app at /opt/seraphinix/apps/gateway
  - Atlantiplex app at /opt/seraphinix/apps/atlantiplex-studio
  - programs/* under /opt/seraphinix/apps/programs
- Install dependencies in each app (npm install)
- Build apps (npm run build) and start (npm start or PM2)

3) Nginx config
- Use bundle-hostinger/nginx-seraphonix.conf as a base
- Copy to /etc/nginx/sites-available/seraphonix and symlink to sites-enabled
- Reload Nginx: sudo nginx -t && sudo systemctl reload nginx

4) TLS
- Run certbot to install TLS certs for verilysovereign.org

5) Persistence
- Setup PostgreSQL per tenant or shared DB with tenant_id tagging (scaling later)

6) Monitoring and backups
- Enable PM2 startup and regular backups for DB

Notes
- This is a baseline for a single domain with a scalable pattern to add more programs.
- To enable multi-domain later, you can add a subdomain for Atlantiplex and adjust Nginx rules.
