# Build stage - compile frontend assets
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files only for better layer caching
COPY package*.json ./

# Install dependencies with BuildKit cache
RUN --mount=type=cache,target=/root/.npm \
    npm install && \
    npm cache clean --force

# Copy source code
COPY . .

# Build production bundle with minification
RUN npm run build

# Remove unnecessary files to reduce final image size
RUN rm -rf \
    .git \
    .gitignore \
    node_modules \
    .eslintrc* \
    .prettierrc* \
    tsconfig*.json \
    vite.config.ts \
    vitest.config.ts \
    *.md \
    src \
    public \
    tests

# Runtime stage - serve with Nginx
FROM nginx:1.25-alpine

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create cache and runtime directories with proper permissions
RUN mkdir -p /var/cache/nginx /var/run/nginx /var/log/nginx && \
    chown -R nginx:nginx /var/cache/nginx /var/run/nginx /var/log/nginx && \
    chmod -R 755 /var/cache/nginx /var/run/nginx

# Copy optimized nginx configuration for SPA with security headers
RUN echo 'server {\n\
    listen 5173 default_server;\n\
    server_name _;\n\
    \n\
    root /usr/share/nginx/html;\n\
    index index.html index.htm;\n\
    \n\
    # Gzip compression for text-based assets\n\
    gzip on;\n\
    gzip_types text/plain text/css application/javascript application/json;\n\
    gzip_vary on;\n\
    gzip_comp_level 6;\n\
    gzip_min_length 1000;\n\
    \n\
    # Security headers\n\
    add_header X-Content-Type-Options "nosniff" always;\n\
    add_header X-Frame-Options "DENY" always;\n\
    add_header X-XSS-Protection "1; mode=block" always;\n\
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;\n\
    \n\
    # SPA routing - serve index.html for all routes\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
        add_header Cache-Control "no-cache, no-store, must-revalidate";\n\
    }\n\
    \n\
    # Cache static assets aggressively\n\
    location ~* \\.(?:js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {\n\
        expires 365d;\n\
        add_header Cache-Control "public, immutable";\n\
        access_log off;\n\
    }\n\
    \n\
    # Health check endpoint\n\
    location /health {\n\
        access_log off;\n\
        return 200 "healthy\\n";\n\
        add_header Content-Type text/plain;\n\
    }\n\
    \n\
    # Deny access to sensitive files\n\
    location ~ /\\. {\n\
        deny all;\n\
        access_log off;\n\
        log_not_found off;\n\
    }\n\
}' > /etc/nginx/conf.d/default.conf

# Copy nginx performance tuning
RUN echo 'user nginx;\n\
worker_processes auto;\n\
error_log /var/log/nginx/error.log warn;\n\
pid /var/run/nginx.pid;\n\
\n\
events {\n\
    worker_connections 1024;\n\
    use epoll;\n\
}\n\
\n\
http {\n\
    include /etc/nginx/mime.types;\n\
    default_type application/octet-stream;\n\
    \n\
    log_format main "$remote_addr - $remote_user [$time_local] \"$request\" "\n\
                    "$status $body_bytes_sent \"$http_referer\" "\n\
                    "\"$http_user_agent\" \"$http_x_forwarded_for\"";\n\
    \n\
    access_log /var/log/nginx/access.log main;\n\
    \n\
    sendfile on;\n\
    tcp_nopush on;\n\
    tcp_nodelay on;\n\
    keepalive_timeout 65;\n\
    types_hash_max_size 2048;\n\
    client_max_body_size 20M;\n\
    \n\
    include /etc/nginx/conf.d/*.conf;\n\
}' > /etc/nginx/nginx.conf

# Copy built frontend from builder stage
COPY --from=builder --chown=nginx:nginx /app/dist /usr/share/nginx/html

# Security: restrict filesystem permissions
RUN chmod -R 555 /usr/share/nginx/html && \
    find /usr/share/nginx/html -type f -exec chmod 444 {} \;

# Set environment variables
ENV NGINX_HOST=_
ENV NGINX_PORT=5173

# Expose port
EXPOSE 5173

# Switch to non-root user
USER nginx

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:5173/health || exit 1

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]
CMD ["nginx", "-g", "daemon off;"]
