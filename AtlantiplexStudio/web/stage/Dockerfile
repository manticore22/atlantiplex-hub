# Node.js Stage Server - Production optimized
# Multi-stage build for minimal image

FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install dependencies with cache mount, exclude dev
RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev --legacy-peer-deps && \
    npm cache clean --force

# Stage 2: Runtime
FROM node:20-alpine

WORKDIR /app

# Install only essential runtime dependencies
RUN apk add --no-cache dumb-init

# Create unprivileged user with restricted shell
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 -h /nonexistent -s /sbin/nologin

# Copy dependencies from builder
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules

# Copy application code
COPY --chown=nodejs:nodejs . .

# Create log and upload directories with correct permissions
RUN mkdir -p /app/logs /app/uploads && \
    chown -R nodejs:nodejs /app

# Metadata
LABEL maintainer="Atlantiplex Team" \
      version="1.0" \
      description="Stage Server - WebSocket & API"

# Environment
ENV NODE_ENV=production \
    NODE_OPTIONS="--max-old-space-size=512"

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 9001

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:9001/health', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})" || exit 1

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
