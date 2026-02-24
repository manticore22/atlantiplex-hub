# Gateway - Central routing and header for all apps
# Multi-stage build for minimal production image
# Monorepo structure: root package.json + workspace gateway

FROM node:20-alpine AS builder

WORKDIR /app

# Copy root lockfiles for dependency caching
COPY package*.json ./

# Use BuildKit cache mount for npm dependencies
RUN --mount=type=cache,target=/root/.npm \
    npm install --omit=dev && \
    npm cache clean --force

# Copy source files and build
COPY shared ./shared
COPY gateway ./gateway

RUN npm run build --workspace=gateway 2>/dev/null || true

# Production stage
FROM node:20-alpine

WORKDIR /app

# Install only dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create unprivileged user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Copy built application and dependencies
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/gateway ./gateway
COPY --from=builder --chown=nodejs:nodejs /app/shared ./shared

# Remove unnecessary files from production image
RUN rm -rf .git .gitignore *.md tests docs

# Metadata labels for production tracking
LABEL maintainer="Atlantiplex Team" \
      version="1.0" \
      description="Gateway - Central routing and headers"

# Production environment
ENV NODE_ENV=production \
    NODE_OPTIONS="--max-old-space-size=256" \
    PORT=3000

EXPOSE 3000

USER nodejs

# Health check with improved logic
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})" || exit 1

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "gateway/server.js"]
