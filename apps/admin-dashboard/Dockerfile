# Admin Dashboard - Management
# Multi-stage build for minimal production image
# Monorepo structure: root package.json + workspace apps

FROM node:20-alpine AS builder

WORKDIR /app

# Copy root lockfiles for dependency caching
COPY package*.json ./

# Use BuildKit cache mount for npm dependencies
RUN --mount=type=cache,target=/root/.npm \
    npm install --omit=dev && \
    npm cache clean --force

# Copy workspace and source
COPY apps/admin-dashboard ./apps/admin-dashboard

RUN npm run build --workspace=apps/admin-dashboard

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
COPY --from=builder --chown=nodejs:nodejs /app/apps/admin-dashboard ./apps/admin-dashboard

# Metadata labels for production tracking
LABEL maintainer="Atlantiplex Team" \
      version="1.0" \
      description="Admin Dashboard - Management UI"

# Production environment
ENV NODE_ENV=production \
    NODE_OPTIONS="--max-old-space-size=512" \
    PORT=5175

EXPOSE 5175

USER nodejs

# Health check with improved timeout
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:5175 || exit 1

ENTRYPOINT ["dumb-init", "--"]
CMD ["npm", "run", "preview", "--workspace=apps/admin-dashboard"]
