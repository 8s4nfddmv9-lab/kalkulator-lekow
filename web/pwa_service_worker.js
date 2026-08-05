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

  // The complete bundle is already present. Do not leave this worker waiting
  // behind an older, partially cached version on Safari or a Home Screen PWA.
  await self.skipWaiting();
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

  // Route subsequent requests from already open clients through the complete
  // cache without forcing a reload or discarding the current form state.
  await self.clients.claim();
}

function navigationDocumentFor(url) {
  const scopeUrl = new URL(self.registration.scope);
  if (url.origin !== scopeUrl.origin || !url.pathname.startsWith(scopeUrl.pathname)) {
    return null;
  }

  const relativePath = url.pathname.slice(scopeUrl.pathname.length);
  if (!relativePath || relativePath === 'index.html') {
    return INDEX_DOCUMENT;
  }
  if (relativePath.endsWith('/')) {
    return `./${relativePath}index.html`;
  }
  return `./${relativePath}`;
}

async function cachedNavigationOrNetwork(request) {
  const cache = await caches.open(CACHE_NAME);
  const navigationDocument = navigationDocumentFor(new URL(request.url));

  if (navigationDocument) {
    const cachedDocument = await cache.match(navigationDocument, {
      ignoreSearch: true,
      ignoreVary: true,
    });
    if (cachedDocument) {
      return cachedDocument;
    }
  }

  try {
    return await fetch(request);
  } catch (networkError) {
    const cachedIndex = await cache.match(INDEX_DOCUMENT, {
      ignoreSearch: true,
      ignoreVary: true,
    });
    if (cachedIndex) {
      return cachedIndex;
    }
    throw networkError;
  }
}

async function cachedAssetOrNetwork(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request, {
    ignoreSearch: true,
    ignoreVary: true,
  });
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
    event.respondWith(cachedNavigationOrNetwork(request));
    return;
  }

  event.respondWith(cachedAssetOrNetwork(request));
});
