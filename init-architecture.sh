#!/bin/bash
# Atlantiplex Hub - Multi-App Architecture Setup
# This script initializes the monolithic app structure with:
# - Shared Gateway (header/router/load balancer)
# - Atlantiplex Studio (creative suite)
# - Product Catalog (e-commerce/shop)
# - Admin Dashboard (management)
# - Dashboard/Social (user engagement)

set -e

echo "🏗️  Setting up Atlantiplex Hub Architecture..."

# Create shared assets and components
echo "📦 Creating shared components..."
mkdir -p ./shared/{components,styles,icons,fonts,utils,constants}

# Create gateway/routing layer
echo "🚪 Creating gateway infrastructure..."
mkdir -p ./gateway/{config,middleware,routes,controllers}

# Initialize each app with standard structure
for APP in atlantiplex-studio product-catalog admin-dashboard dashboard-social; do
  echo "📁 Initializing $APP..."
  
  # Create app structure
  mkdir -p ./apps/$APP/{src/{components,pages,services,hooks,types},public,dist}
  mkdir -p ./apps/$APP/config
  mkdir -p ./apps/$APP/tests
  
  # Create package.json for each app
  cat > ./apps/$APP/package.json << EOF
{
  "name": "@atlantiplex/$APP",
  "version": "1.0.0",
  "description": "Atlantiplex Hub - $APP",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest",
    "lint": "eslint src --ext .ts,.tsx"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.0",
    "vite": "^5.0.0"
  }
}
EOF

  # Create .gitignore
  cat > ./apps/$APP/.gitignore << EOF
# Dependencies
node_modules/
/.pnp
.pnp.js

# Testing
/coverage

# Production
/dist
/build

# Misc
.DS_Store
.env.local
.env.*.local

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*
EOF

  # Create README
  cat > ./apps/$APP/README.md << EOF
# $APP

Part of the Atlantiplex Hub multi-app architecture.

## Quick Start

\`\`\`bash
npm install
npm run dev
\`\`\`

## Building

\`\`\`bash
npm run build
\`\`\`
EOF

done

echo "✅ Architecture initialized!"
echo ""
echo "📋 Structure created:"
echo "  ./shared/           - Shared components, styles, utilities"
echo "  ./gateway/          - Central routing and load balancing"
echo "  ./apps/"
echo "    ├── atlantiplex-studio"
echo "    ├── product-catalog"
echo "    ├── admin-dashboard"
echo "    └── dashboard-social"
echo ""
echo "Next steps:"
echo "  1. npm install in each app directory"
echo "  2. Configure gateway routing"
echo "  3. Set up shared component exports"
echo "  4. Configure docker-compose for multi-app deployment"
