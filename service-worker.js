const CACHE_NAME = 'cozy-hay-farm-v2';
const CORE_ASSETS = [
    './',
    './index.html',
    './manifest.json',
    './icon-192.png',
    './icon-512.png',
    './favicon.ico'
];

// Install: pre-cache core offline assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(CORE_ASSETS).catch(err => {
                console.warn('Some core assets failed to cache:', err);
            });
        }).then(() => self.skipWaiting())
    );
});

// Activate: clean up older caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch: Serve from cache or network, bypass API requests
self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);

    // Bypass API calls (never cache live server sync endpoints regardless of domain or subpath)
    if (url.pathname.startsWith('/api/') || url.pathname.includes('/api/')) {
        return;
    }

    // Only cache GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    event.respondWith(
        caches.match(event.request).then(cachedResponse => {
            if (cachedResponse) {
                // Return cached version immediately, but fetch update in background (Stale-While-Revalidate)
                fetch(event.request).then(networkResponse => {
                    if (networkResponse && networkResponse.status === 200) {
                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(event.request, networkResponse.clone());
                        });
                    }
                }).catch(() => {});
                return cachedResponse;
            }

            // Not in cache, fetch from network and cache
            return fetch(event.request).then(networkResponse => {
                if (!networkResponse || networkResponse.status !== 200 || networkResponse.type === 'opaque') {
                    return networkResponse;
                }
                const responseClone = networkResponse.clone();
                caches.open(CACHE_NAME).then(cache => {
                    cache.put(event.request, responseClone);
                });
                return networkResponse;
            }).catch(() => {
                // If offline and request is for page navigation, fallback to index.html
                if (event.request.mode === 'navigate') {
                    return caches.match('./index.html');
                }
            });
        })
    );
});
