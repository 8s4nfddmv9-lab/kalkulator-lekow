const CACHE_PREFIX = 'infusioncalc-pwa-';
const LEGACY_CACHE_PREFIXES = ['kalkulator-lekow-'];
const CACHE_NAME = 'infusioncalc-pwa-__BUILD_ID__';
const INDEX_DOCUMENT = './index.html';
const OFFLINE_FILES = __OFFLINE_FILES__;

async function installOfflineBundle() {
  const cache = await caches.open(CACHE_NAME);
  const requests = OFFLINE_FILES.map(
    (url) => new Request(url, {
      cache: 'reload',
      credentials: 'same-origin',
    }),
  );

  try {
    await cache.addAll(requests);
  } catch (error) {
    await caches.delete(CACHE_NAME);
    throw error;
  }
}

async function activateOfflineBundle() {
  const managedPrefixes = [CACHE_PREFIX, ...LEGACY_CACHE_PREFIXES];
  const keys = await caches.keys();
  await Promise.all(
    keys
      .filter(
        (key) => key !== CACHE_NAME &&
          managedPrefixes.some((prefix) => key.startsWith(prefix)),
      )
      .map((key) => caches.delete(key)),
  );
}

async function cachedIndexOrNetwork(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(INDEX_DOCUMENT, { ignoreSearch: true });
  if (cached) {
    return cached;
  }
  return fetch(request);
}

async function cachedAssetOrNetwork(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request, { ignoreSearch: true });
  if (cached) {
    return cached;
  }
  return fetch(request);
}

self.addEventListener('install', (event) => {
  event.waitUntil(installOfflineBundle());
});

self.addEventListener('activate', (event) => {
  event.waitUntil(activateOfflineBundle());
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') {
    return;
  }

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) {
    return;
  }

  if (request.mode === 'navigate') {
    event.respondWith(cachedIndexOrNetwork(request));
    return;
  }

  event.respondWith(cachedAssetOrNetwork(request));
});
