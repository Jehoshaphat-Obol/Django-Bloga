// Define a cache name and the files you want to cache
const CACHE_NAME = 'my-site-cache-v1';
const urlsToCache = [
  '/',
  '/static/css/main.css', // Example: Path to your main CSS file
  '/static/js/main.js',   // Example: Path to your main JS file
  '/static/images/logo.png', // Example: Path to logo or other static assets
];

// Install event: Caching resources during the installation phase
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event: Intercepts network requests and serves cached resources if available
self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Cache hit - return the cached response
        if (response) {
          return response;
        }
        return fetch(event.request); // Fallback to network if not cached
      })
  );
});

// Activate event: Clean up old caches if there are any updates
self.addEventListener('activate', function(event) {
  const cacheWhitelist = [CACHE_NAME];
  
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
