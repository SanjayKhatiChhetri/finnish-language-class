const CACHE_NAME = 'classroom-ai-cache-v1';
const APP_SHELL_URLS = [
  '/',
  '/index.html',
  '/index.css',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
];

// On install, cache the app shell
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache and caching app shell');
        return cache.addAll(APP_SHELL_URLS);
      })
      .then(() => self.skipWaiting())
  );
});

// On activate, clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// On fetch, use a cache-first strategy
self.addEventListener('fetch', event => {
  const { request } = event;

  // Don't cache API calls to Google
  if (request.url.includes('generativelanguage.googleapis.com')) {
    event.respondWith(fetch(request));
    return;
  }

  event.respondWith(
    caches.match(request).then(cachedResponse => {
      // Return from cache if found
      if (cachedResponse) {
        return cachedResponse;
      }
      
      // If not in cache, fetch from network and add to cache
      return fetch(request).then(networkResponse => {
        // Check if we received a valid response to cache
        if (networkResponse && networkResponse.status === 200) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(request, responseToCache);
          });
        }
        return networkResponse;
      }).catch(error => {
        console.error('Fetch failed:', error);
        // In a real app, you might want to return a fallback offline page here.
      });
    })
  );
});