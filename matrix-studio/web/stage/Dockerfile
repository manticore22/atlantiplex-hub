# Multi-stage Dockerfile for Node.js production application
FROM node:22-slim AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with BuildKit cache
RUN --mount=type=cache,target=/root/.npm \
    npm ci --production && \
    npm cache clean --force

# Copy application source code
COPY . .

# Runtime stage - minimal production image
FROM node:22-slim

WORKDIR /app

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Copy everything from builder (node_modules + code)
COPY --from=builder --chown=nodejs:nodejs /app . 

# Exclude unnecessary files to reduce layer size
RUN rm -rf \
    .git \
    .gitignore \
    .npm \
    .eslintrc* \
    tsconfig*.json \
    *.md \
    tests \
    docs \
    coverage

# Create application directories with proper permissions
RUN mkdir -p logs uploads && \
    chown -R nodejs:nodejs logs uploads . && \
    chmod 755 logs uploads

# Set environment variables
ENV NODE_ENV=production \
    NODE_OPTIONS="--max-old-space-size=512 --no-deprecation" \
    PORT=9001

# Expose port
EXPOSE 9001

# Switch to non-root user
USER nodejs

# Health check - using node built-in http client
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:' + process.env.PORT, (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})" || exit 1

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
