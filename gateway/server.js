// Gateway Server - Routes all traffic and serves shared header
import express from 'express';
import { createProxyMiddleware } from 'express-http-proxy';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 3000;

// Serve shared assets
app.use('/shared', express.static(path.join(__dirname, '../shared')));

// App routing configuration
const apps = [
  {
    path: '/studio',
    target: process.env.VITE_STUDIO_URL || 'http://localhost:5173',
    name: 'Atlantiplex Studio'
  },
  {
    path: '/products',
    target: process.env.VITE_CATALOG_URL || 'http://localhost:5174',
    name: 'Product Catalog'
  },
  {
    path: '/admin',
    target: process.env.VITE_ADMIN_URL || 'http://localhost:5175',
    name: 'Admin Dashboard'
  },
  {
    path: '/dashboard',
    target: process.env.VITE_DASHBOARD_URL || 'http://localhost:5176',
    name: 'Dashboard & Social'
  }
];

// Register proxy routes for each app
apps.forEach(({ path: appPath, target }) => {
  app.use(
    appPath,
    createProxyMiddleware({
      target,
      changeOrigin: true,
      pathRewrite: {
        [`^${appPath}`]: ''
      },
      onError: (err, req, res) => {
        console.error(`Error routing to ${target}:`, err.message);
        res.status(503).json({
          error: 'Service temporarily unavailable',
          timestamp: new Date().toISOString()
        });
      }
    })
  );
});

// API proxy
app.use('/api', createProxyMiddleware({
  target: process.env.VITE_API_BASE || 'http://localhost:5000',
  changeOrigin: true
}));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Root route - serves gateway info
app.get('/', (req, res) => {
  res.json({
    name: 'Atlantiplex Hub Gateway',
    version: '1.0.0',
    description: 'Unified entry point for Atlantiplex multi-app platform',
    apps: apps.map(({ path: appPath, name }) => ({
      name,
      route: appPath
    })),
    api: '/api'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    path: req.originalUrl,
    message: 'Route not found in gateway'
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Gateway error:', err);
  res.status(500).json({
    error: 'Internal Server Error',
    timestamp: new Date().toISOString()
  });
});

app.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════╗
║         ATLANTIPLEX HUB GATEWAY                ║
║              Listening on port ${PORT}              ║
╚════════════════════════════════════════════════╝

📍 Available Routes:
  ${apps.map(({ path: appPath, name }) => `  🔗 ${appPath} → ${name}`).join('\n  ')}
  📡 /api → Backend API Server

🎯 Access the platform at: http://localhost:${PORT}
  `);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM signal received: closing HTTP server');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('SIGINT signal received: closing HTTP server');
  process.exit(0);
});
