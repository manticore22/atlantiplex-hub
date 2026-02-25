# Frontend nginx server - Production optimized
# Multi-stage build for minimal, secure image

FROM node:22-slim AS builder

WORKDIR /app

# Copy and install dependencies
COPY package*.json ./

RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev && \
    npm cache clean --force

# Copy source and build
COPY . .
RUN npm run build

# Production stage - use nginx alpine
FROM nginx:1.27-bullseye-slim

WORKDIR /etc/nginx

# Remove default nginx configs
RUN rm -f /etc/nginx/conf.d/default.conf

# Copy optimized nginx configuration
RUN cat > /etc/nginx/conf.d/production.conf <<'NGINXEOF'
server {
    listen 80 default_server;
    server_name _;
    
    root /usr/share/nginx/html;
    index index.html;

    # Enable gzip compression
    gzip on;
    gzip_types text/css text/javascript application/javascript application/json text/xml text/plain;
    gzip_min_length 1000;
    gzip_comp_level 6;
    gzip_proxied any;
    gzip_vary on;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    # Cache static assets (long-lived)
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # SPA fallback - serve index.html for all routes
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, must-revalidate, max-age=0";
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy";
        add_header Content-Type text/plain;
    }

    # Deny access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ \.env {
        deny all;
        access_log off;
        log_not_found off;
    }
}
NGINXEOF

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Metadata labels for production tracking
LABEL maintainer="Atlantiplex Team" \
      version="1.0" \
      description="AtlantiplexStudio Frontend"

EXPOSE 80

# Health check with native curl
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Run nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
