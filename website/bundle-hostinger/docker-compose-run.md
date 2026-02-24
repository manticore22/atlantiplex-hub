Hostinger Docker Compose Run Guide

- Build and run the multi-app stack: gateway and Atlantiplex behind Nginx
- Commands:
  1) docker-compose -f docker-compose.yml up -d --build
  2) docker-compose ps
  3) curl -I http://your-domain/
  4) curl -I http://your-domain/atlantiplex/
- TLS: configure TLS with Certbot against your domain after Nginx is running
- Logs: docker logs -f gateway, docker logs -f atlantiplex, docker logs -f nginx
