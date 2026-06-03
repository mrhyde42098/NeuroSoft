/* NeuroSoft Service Worker — Offline-first PWA
 *
 * IMPORTANTE: cualquier cambio en el bundle/JS/CSS requiere bumpear
 * CACHE_NAME para que el handler `activate` borre las cachés viejas
 * y los clientes reciban los assets nuevos. Sin bump, el service
 * worker sigue sirviendo la versión cacheada (estrategia cache-first).
 *
 * §sw-fix-2026-05: BUMP forzoso porque versiones anteriores del SW
 *   cachearon /index.html apuntando a hashes obsoletos, lo que dejaba
 *   la app en pantalla blanca al primer arranque tras una actualización.
 *   Esta versión:
 *     - usa cache name "neurosoft-v5-editorial"
 *     - NO precarga /index.html (siempre network-first)
 *     - elimina TODAS las cachés que empiecen por "neurosoft-" al activarse
 *     - hace un purge defensivo del SW si /assets/index-*.js devuelve 404
 */
const CACHE_NAME = "neurosoft-v5-editorial";
const CORE_ASSETS = [
  "/manifest.json",
  "https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap",
  "https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&display=swap",
  "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap",
];

/* Install: precache solo assets estáticos externos (no HTML).
 * §sw-fix: NO cacheamos /index.html ni / aquí — esos van por
 * navegación network-first para que un bump de versión llegue siempre. */
self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) =>
      Promise.all(
        CORE_ASSETS.map((url) =>
          cache.add(url).catch(() => {})
        )
      )
    )
  );
  self.skipWaiting();
});

/* Activate: purga TODAS las cachés con prefijo "neurosoft-" que no
 * coincidan con el name actual. Esto garantiza que al actualizar la
 * app, las versiones antiguas se invalidan completamente. */
self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k.startsWith("neurosoft-") && k !== CACHE_NAME)
          .map((k) => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

/* Fetch strategy:
 *   API           → network-only (con respuesta offline JSON si falla)
 *   navegaciones  → network-first (HTML siempre fresco)
 *   /assets/*     → network-first (Vite hashes — fresh > cache)
 *   resto         → cache-first (fuentes externas, etc.)
 */
self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);

  // ── API requests: network-only ──
  if (url.port === "8000" || url.pathname.startsWith("/api/")) {
    e.respondWith(
      fetch(e.request).catch(() =>
        new Response(
          JSON.stringify({
            offline: true,
            detail: "Sin conexión al servidor. Los datos se mostrarán cuando vuelva la conexión.",
          }),
          { status: 503, headers: { "Content-Type": "application/json" } }
        )
      )
    );
    return;
  }

  // ── HTML navigations: network-first, cache fallback ──
  if (e.request.mode === "navigate" || e.request.destination === "document") {
    e.respondWith(
      fetch(e.request)
        .then((res) => {
          // Solo cacheamos respuestas exitosas (no 5xx ni 404).
          if (res.ok) {
            const clone = res.clone();
            caches.open(CACHE_NAME).then((c) =>
              c.put(e.request, clone).catch(() => {})
            );
          }
          return res;
        })
        .catch(() =>
          caches.match(e.request).then((r) => r || caches.match("/index.html"))
        )
    );
    return;
  }

  // ── Bundles JS/CSS de Vite (hash en el nombre) → network-first ──
  if (
    url.pathname.startsWith("/assets/") &&
    /\.(js|css|woff2?)$/.test(url.pathname)
  ) {
    e.respondWith(
      fetch(e.request)
        .then((res) => {
          // §sw-fix: si el asset hasheado retorna 404, casi siempre significa
          // que la página cacheada está apuntando a hashes obsoletos.
          // Purgamos la caché entera y notificamos al cliente.
          if (res.status === 404) {
            caches.delete(CACHE_NAME);
            self.clients.matchAll().then((cs) =>
              cs.forEach((c) => c.postMessage({ type: "STALE_BUNDLE_DETECTED" }))
            );
          }
          if (res.ok) {
            const clone = res.clone();
            caches.open(CACHE_NAME).then((c) =>
              c.put(e.request, clone).catch(() => {})
            );
          }
          return res;
        })
        .catch(() =>
          caches.match(e.request).then((r) => r || new Response("", { status: 504 }))
        )
    );
    return;
  }

  // ── Otros estáticos (fuentes externas, CDN, manifest): cache-first ──
  e.respondWith(
    caches.match(e.request).then((cached) => {
      if (cached) return cached;
      return fetch(e.request).then((res) => {
        if (res.ok && (res.type === "basic" || res.type === "cors")) {
          const clone = res.clone();
          caches.open(CACHE_NAME).then((c) => c.put(e.request, clone).catch(() => {}));
        }
        return res;
      }).catch(() => new Response("", { status: 504 }));
    })
  );
});

/* Listen for messages — SKIP_WAITING (update flow) + manual purge */
self.addEventListener("message", (e) => {
  if (!e.data) return;
  if (e.data.type === "SKIP_WAITING") self.skipWaiting();
  if (e.data.type === "PURGE_CACHE") {
    caches.keys().then((keys) =>
      Promise.all(keys.map((k) => caches.delete(k)))
    );
  }
});
