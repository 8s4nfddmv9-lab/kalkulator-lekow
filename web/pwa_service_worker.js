const CACHE_PREFIX = 'infusioncalc-';
const CACHE_NAME = `${CACHE_PREFIX}__BUILD_ID__`;
const OFFLINE_INDEX = './index.html';
const OFFLINE_ASSETS = __OFFLINE_ASSETS__;

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);

    // cache.addAll is intentionally atomic from the service worker's point of
    // view: this version must not become active without its complete app shell.
    await cache.addAll(OFFLINE_ASSETS);
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(
      keys
        .filter((key) => key.startsWith(CACHE_PREFIX) && key !== CACHE_NAME)
        .map((key) => caches.delete(key)),
    );
    await self.clients.claim();
  })());
});

function isCacheable(response) {
  return response &&
    response.status === 200 &&
    (response.type === 'basic' || response.type === 'default');
}

async function cacheResponse(cacheKey, response) {
  if (!isCacheable(response)) return;

  const cache = await caches.open(CACHE_NAME);
  await cache.put(cacheKey, response.clone());
}

async function handleNavigation(request) {
  try {
    const response = await fetch(request);
    if (!response.ok) {
      throw new Error(`Navigation request failed with ${response.status}.`);
    }
    await cacheResponse(OFFLINE_INDEX, response);
    return response;
  } catch (_) {
    const cached = await caches.match(OFFLINE_INDEX);
    if (cached) return cached;

    return new Response('InfusionCalc nie jest jeszcze gotowy do pracy offline.', {
      status: 503,
      headers: {'Content-Type': 'text/plain; charset=utf-8'},
    });
  }
}

async function handleAsset(request) {
  const cached = await caches.match(request);
  if (cached) return cached;

  const response = await fetch(request);
  await cacheResponse(request, response);
  return response;
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.mode === 'navigate') {
    event.respondWith(handleNavigation(request));
    return;
  }

  event.respondWith(handleAsset(request));
});
