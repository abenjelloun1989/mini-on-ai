/**
 * service-worker.js — offline shell.
 *  - Precache the static app shell on install.
 *  - Cache-first for static assets (instant load).
 *  - Network-first for /api/* (fall through to cache when offline).
 */
const CACHE = "finances-v1";
const SHELL = [
  "./",
  "./index.html",
  "./manifest.json",
  "./css/style.css",
  "./vendor/chart.umd.min.js",
  "./js/app.js",
  "./js/api.js",
  "./js/ui.js",
  "./js/store.js",
  "./js/screens/accueil.js",
  "./js/screens/add-tx.js",
  "./js/screens/historique.js",
  "./js/screens/stats.js",
  "./js/screens/reserves.js",
  "./js/screens/chat.js",
  "./js/screens/reglages.js",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const { request } = e;
  if (request.method !== "GET") return;
  const url = new URL(request.url);

  // API: network-first, fall back to cache (read-only endpoints) when offline.
  if (url.pathname.startsWith("/api/")) {
    e.respondWith(
      fetch(request)
        .then((resp) => {
          const copy = resp.clone();
          caches.open(CACHE).then((c) => c.put(request, copy)).catch(() => {});
          return resp;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // Static: cache-first.
  e.respondWith(
    caches.match(request).then((cached) =>
      cached ||
      fetch(request).then((resp) => {
        const copy = resp.clone();
        caches.open(CACHE).then((c) => c.put(request, copy)).catch(() => {});
        return resp;
      }).catch(() => caches.match("./index.html"))
    )
  );
});
