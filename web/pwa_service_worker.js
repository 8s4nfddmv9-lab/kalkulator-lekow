const CACHE_PREFIX = 'infusioncalc-pwa-';
const LEGACY_CACHE_PREFIXES = ['kalkulator-lekow-'];
const CACHE_NAME = 'infusioncalc-pwa-__BUILD_ID__';
const INDEX_DOCUMENT = './index.html';
const NOT_FOUND_DOCUMENT = './404.html';
const OFFLINE_FILES = __OFFLINE_FILES__;

const CANONICAL_DOCUMENTS = new Map([
  ['', INDEX_DOCUMENT],
  ['about/', './about/index.html'],
  ['privacy/', './privacy/index.html'],
  ['changelog/', './changelog/index.html'],
  ['404.html', NOT_FOUND_DOCUMENT],
]);

const CANONICAL_REDIRECTS = new Map([
  ['index.html', ''],
  ['about', 'about/'],
  ['about/index.html', 'about/'],
  ['privacy', 'privacy/'],
  ['privacy/index.html', 'privacy/'],
  ['changelog', 'changelog/'],
  ['changelog/index.html', 'changelog/'],
]);

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

function relativeNavigationPath(url) {
  const scopeUrl = new URL(self.registration.scope);
  if (url.origin !== scopeUrl.origin || !url.pathname.startsWith(scopeUrl.pathname)) {
    return null;
  }
  return url.pathname.slice(scopeUrl.pathname.length);
}

function canonicalRedirectFor(url) {
  const relativePath = relativeNavigationPath(url);
  if (relativePath === null || !CANONICAL_REDIRECTS.has(relativePath)) {
    return null;
  }

  const scopeUrl = new URL(self.registration.scope);
  const canonicalPath = CANONICAL_REDIRECTS.get(relativePath);
  const redirectUrl = new URL(canonicalPath || './', scopeUrl);
  redirectUrl.search = url.search;
  return redirectUrl;
}

function navigationDocumentFor(url) {
  const relativePath = relativeNavigationPath(url);
  if (relativePath === null) {
    return null;
  }
  return CANONICAL_DOCUMENTS.get(relativePath) || null;
}

async function cachedNotFoundResponse(cache) {
  const cached = await cache.match(NOT_FOUND_DOCUMENT, {
    ignoreSearch: true,
    ignoreVary: true,
  });
  if (!cached) {
    return null;
  }

  const headers = new Headers(cached.headers);
  headers.set('Content-Type', 'text/html; charset=utf-8');
  headers.set('Cache-Control', 'no-store');
  return new Response(await cached.text(), {
    status: 404,
    statusText: 'Not Found',
    headers,
  });
}

async function cachedNavigationOrNetwork(request) {
  const cache = await caches.open(CACHE_NAME);
  const url = new URL(request.url);
  const redirectUrl = canonicalRedirectFor(url);
  if (redirectUrl) {
    return Response.redirect(redirectUrl.href, 308);
  }

  const navigationDocument = navigationDocumentFor(url);
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
    const notFound = await cachedNotFoundResponse(cache);
    if (notFound) {
      return notFound;
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
