# Multi-stage Dockerfile for Node.js Stage Server
# Stage 1: Dependencies
FROM node:20-alpine AS dependencies
WORKDIR /app

COPY package*.json ./

# Install dependencies excluding optional packages (heapdump is optional)
# Use --no-optional and --legacy-peer-deps for compatibility
RUN npm ci --no-optional --legacy-peer-deps && npm cache clean --force

# Stage 2: Runtime
FROM node:20-alpine
WORKDIR /app

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Copy dependencies from builder stage (node:20-alpine already has node user)
COPY --from=dependencies --chown=node:node /app/node_modules ./node_modules

# Copy application code
COPY --chown=node:node . .

# Create log and upload directories
RUN mkdir -p /app/logs /app/uploads && \
    chown -R node:node /app

# Switch to non-root user
USER node

# Expose port
EXPOSE 9001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:9001/health || exit 1

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
