const CACHE_NAME = 'atlantiplex-studio-v2.5.0';
const STATIC_CACHE = 'static-v2.5.0';
const DYNAMIC_CACHE = 'dynamic-v2.5.0';
const RUNTIME_CACHE = 'runtime-v2.5.0';

// Assets to cache immediately
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/offline.html',
  '/robots.txt',
  
  // CSS
  '/css/design-system.css',
  '/css/components.css',
  '/css/accessibility.css',
  
  // JavaScript
  '/js/app.js',
  '/js/vendor.js',
  
  // Images
  '/icons/icon-72x72.png',
  '/icons/icon-96x96.png',
  '/icons/icon-128x128.png',
  '/icons/icon-144x144.png',
  '/icons/icon-152x152.png',
  '/icons/icon-192x192.png',
  '/icons/icon-384x384.png',
  '/icons/icon-512x512.png',
  
  // Fonts
  '/fonts/inter-regular.woff2',
  '/fonts/inter-medium.woff2',
  '/fonts/inter-semibold.woff2',
  '/fonts/inter-bold.woff2',
  '/fonts/poppins-regular.woff2',
  '/fonts/poppins-semibold.woff2',
  
  // Critical API responses
  '/api/user/profile',
  '/api/stream/status'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker v2.5.0');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('[SW] Static assets cached successfully');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('[SW] Failed to cache static assets:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker v2.5.0');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && 
                cacheName !== DYNAMIC_CACHE && 
                cacheName !== RUNTIME_CACHE) {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('[SW] Old caches cleaned up');
        return self.clients.claim();
      })
      .then(() => {
        // Notify all clients about the update
        return self.clients.matchAll().then((clients) => {
          clients.forEach((client) => {
            client.postMessage({ type: 'SW_UPDATED' });
          });
        });
      })
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip external requests (except specific trusted domains)
  if (!url.origin.includes(self.location.origin) && 
      !url.origin.includes('fonts.googleapis.com') &&
      !url.origin.includes('fonts.gstatic.com')) {
    return;
  }
  
  // Handle different types of requests
  if (url.pathname.includes('/api/')) {
    // API requests - Network first, fallback to cache
    event.respondWith(handleApiRequest(request));
  } else if (isStaticAsset(request)) {
    // Static assets - Cache first
    event.respondWith(handleStaticAsset(request));
  } else if (url.pathname.includes('/stream/') || 
             url.pathname.includes('/recording/')) {
    // Streaming content - Network only with cache fallback
    event.respondWith(handleStreamContent(request));
  } else {
    // Navigation requests - HTML files
    event.respondWith(handleNavigation(request));
  }
});

// Handle API requests with network-first strategy
async function handleApiRequest(request) {
  const cache = await caches.open(DYNAMIC_CACHE);
  
  try {
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      const responseClone = networkResponse.clone();
      await cache.put(request, responseClone);
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed, trying cache:', request.url);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline fallback for specific API endpoints
    if (request.url.includes('/api/user/profile')) {
      return new Response(JSON.stringify({
        id: 'offline-user',
        name: 'Offline User',
        status: 'offline'
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    throw error;
  }
}

// Handle static assets with cache-first strategy
async function handleStaticAsset(request) {
  const cache = await caches.open(STATIC_CACHE);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const responseClone = networkResponse.clone();
      await cache.put(request, responseClone);
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Static asset fetch failed:', request.url);
    throw error;
  }
}

// Handle streaming content
async function handleStreamContent(request) {
  const cache = await caches.open(RUNTIME_CACHE);
  
  try {
    const networkResponse = await fetch(request);
    
    // Cache streaming content for offline viewing
    if (networkResponse.ok) {
      const responseClone = networkResponse.clone();
      await cache.put(request, responseClone);
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Stream content fetch failed, trying cache');
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline fallback for stream content
    return new Response(JSON.stringify({
      error: 'Content not available offline',
      message: 'This content requires an internet connection'
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Handle navigation requests
async function handleNavigation(request) {
  const cache = await caches.open(STATIC_CACHE);
  
  try {
    const networkResponse = await fetch(request);
    
    // Cache HTML responses
    if (networkResponse.ok && networkResponse.headers.get('Content-Type')?.includes('text/html')) {
      const responseClone = networkResponse.clone();
      await cache.put(request, responseClone);
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Navigation failed, trying cache');
    
    // Try to serve from cache
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Fallback to offline page
    const offlineResponse = await cache.match('/offline.html');
    if (offlineResponse) {
      return offlineResponse;
    }
    
    // Basic offline fallback
    return new Response(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Offline - Atlantiplex Studio</title>
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <style>
            body { font-family: system-ui; padding: 2rem; text-align: center; }
            .offline-icon { font-size: 4rem; margin-bottom: 1rem; }
          </style>
        </head>
        <body>
          <div class="offline-icon">📡</div>
          <h1>You're offline</h1>
          <p>Please check your internet connection and try again.</p>
        </body>
      </html>
    `, {
      status: 200,
      headers: { 'Content-Type': 'text/html' }
    });
  }
}

// Check if request is for a static asset
function isStaticAsset(request) {
  const url = new URL(request.url);
  const staticExtensions = [
    '.css', '.js', '.woff', '.woff2', '.ttf', '.eot',
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp',
    '.ico', '.json', '.xml'
  ];
  
  return staticExtensions.some(ext => url.pathname.endsWith(ext));
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync triggered:', event.tag);
  
  if (event.tag === 'background-sync-streams') {
    event.waitUntil(syncOfflineStreams());
  } else if (event.tag === 'background-sync-analytics') {
    event.waitUntil(syncOfflineAnalytics());
  }
});

// Sync offline stream data
async function syncOfflineStreams() {
  try {
    const cache = await caches.open(RUNTIME_CACHE);
    const offlineStreams = await cache.match('/offline-streams');
    
    if (offlineStreams) {
      const streams = await offlineStreams.json();
      
      for (const stream of streams) {
        try {
          await fetch('/api/stream/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(stream)
          });
        } catch (error) {
          console.error('[SW] Failed to sync stream:', stream.id, error);
        }
      }
      
      // Clear synced streams
      await cache.delete('/offline-streams');
    }
  } catch (error) {
    console.error('[SW] Background sync failed:', error);
  }
}

// Sync offline analytics data
async function syncOfflineAnalytics() {
  try {
    const cache = await caches.open(RUNTIME_CACHE);
    const offlineEvents = await cache.match('/offline-analytics');
    
    if (offlineEvents) {
      const events = await offlineEvents.json();
      
      for (const event of events) {
        try {
          await fetch('/api/analytics/track', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(event)
          });
        } catch (error) {
          console.error('[SW] Failed to sync analytics event:', event.id, error);
        }
      }
      
      // Clear synced events
      await cache.delete('/offline-analytics');
    }
  } catch (error) {
    console.error('[SW] Analytics sync failed:', error);
  }
}

// Push notification handling
self.addEventListener('push', (event) => {
  console.log('[SW] Push message received');
  
  const options = {
    body: 'You have a new notification from Atlantiplex Studio',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View',
        icon: '/icons/checkmark.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/icons/xmark.png'
      }
    ],
    requireInteraction: true,
    silent: false
  };

  if (event.data) {
    const data = event.data.json();
    options.title = data.title || 'Atlantiplex Studio';
    options.body = data.body || options.body;
    options.data = { ...options.data, ...data };
  }

  event.waitUntil(
    self.registration.showNotification(options.title || 'Atlantiplex Studio', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification click received');
  
  event.notification.close();

  if (event.action === 'explore') {
    // Open the app to relevant content
    event.waitUntil(
      clients.openWindow(event.notification.data.url || '/')
    );
  } else if (event.action === 'close') {
    // Just close the notification
    return;
  } else {
    // Default action - open app
    event.waitUntil(
      clients.matchAll().then((clientList) => {
        for (const client of clientList) {
          if (client.url === '/' && 'focus' in client) {
            return client.focus();
          }
        }
        if (clients.openWindow) {
          return clients.openWindow('/');
        }
      })
    );
  }
});

// Handle notification close
self.addEventListener('notificationclose', (event) => {
  console.log('[SW] Notification closed');
  
  // Log notification dismissal for analytics
  event.waitUntil(
    fetch('/api/analytics/notification-dismissed', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        notificationId: event.notification.data.primaryKey,
        timestamp: Date.now()
      })
    }).catch(() => {
      // Ignore errors during analytics tracking
    })
  );
});

// Periodic background sync for content updates
self.addEventListener('periodicsync', (event) => {
  console.log('[SW] Periodic sync triggered:', event.tag);
  
  if (event.tag === 'update-content') {
    event.waitUntil(updateCachedContent());
  } else if (event.tag === 'cleanup-cache') {
    event.waitUntil(cleanupOldCache());
  }
});

// Update cached content periodically
async function updateCachedContent() {
  try {
    const cache = await caches.open(STATIC_CACHE);
    
    for (const asset of STATIC_ASSETS) {
      try {
        const response = await fetch(asset);
        if (response.ok) {
          await cache.put(asset, response);
        }
      } catch (error) {
        console.log('[SW] Failed to update asset:', asset);
      }
    }
    
    console.log('[SW] Content update completed');
  } catch (error) {
    console.error('[SW] Content update failed:', error);
  }
}

// Clean up old cache entries
async function cleanupOldCache() {
  try {
    const cache = await caches.open(DYNAMIC_CACHE);
    const requests = await cache.keys();
    
    for (const request of requests) {
      const response = await cache.match(request);
      const dateHeader = response?.headers.get('date');
      
      if (dateHeader) {
        const responseDate = new Date(dateHeader);
        const daysSinceCache = (Date.now() - responseDate.getTime()) / (1000 * 60 * 60 * 24);
        
        // Remove entries older than 30 days
        if (daysSinceCache > 30) {
          await cache.delete(request);
        }
      }
    }
    
    console.log('[SW] Cache cleanup completed');
  } catch (error) {
    console.error('[SW] Cache cleanup failed:', error);
  }
}

// Message handling from client
self.addEventListener('message', (event) => {
  console.log('[SW] Message received from client:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  } else if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: '2.5.0' });
  } else if (event.data && event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(clearAllCaches());
  }
});

// Clear all caches
async function clearAllCaches() {
  const cacheNames = await caches.keys();
  return Promise.all(
    cacheNames.map(cacheName => caches.delete(cacheName))
  );
}

// Error handling
self.addEventListener('error', (event) => {
  console.error('[SW] Service worker error:', event.error);
});

self.addEventListener('unhandledrejection', (event) => {
  console.error('[SW] Unhandled promise rejection:', event.reason);
});