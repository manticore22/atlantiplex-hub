# Admin Dashboard - Management UI
# Production-optimized multi-stage build

FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install dependencies with cache mount
RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev && \
    npm cache clean --force

# Copy source
COPY . .

# Build application
RUN npm run build

# Production runtime stage
FROM node:20-alpine

WORKDIR /app

# Install only essential runtime dependencies
RUN apk add --no-cache dumb-init

# Create unprivileged user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 -h /nonexistent -s /sbin/nologin

# Copy production dependencies and built app
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/package*.json ./

# Metadata
LABEL maintainer="Atlantiplex Team" \
      version="1.0" \
      description="Admin Dashboard - Management UI"

# Environment
ENV NODE_ENV=production \
    PORT=5175 \
    NODE_OPTIONS="--max-old-space-size=512"

EXPOSE 5175

USER nodejs

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:5175', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})" || exit 1

ENTRYPOINT ["dumb-init", "--"]
CMD ["npm", "run", "preview"]
