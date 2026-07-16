/* Sistema Oliveira — Service Worker
   Estratégia:
   - App (navegação): network-first → cai pro cache quando offline (garante atualização + offline)
   - CDNs (fontes, flatpickr): cache-first com runtime cache (2ª vez abre offline)
   - Google (identity/drive/apis): NUNCA cacheia — precisa de rede, não pode servir stale
   Ao publicar uma nova versão do sistema, suba o número em CACHE. */
const CACHE = "oliveira-v1";
const APP_SHELL = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icon-192.png",
  "./icon-512.png",
  "./icon-maskable-512.png",
  "./apple-touch-icon.png"
];

// Domínios que dependem de rede e não devem ser cacheados
const NO_CACHE = [
  "accounts.google.com",
  "apis.google.com",
  "googleapis.com",
  "google.com/gsi",
  "gstatic.com/recaptcha"
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(APP_SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);

  // Nunca interceptar chamadas do Google (login/drive) — deixa passar direto pra rede
  if (NO_CACHE.some((d) => url.hostname.includes(d) || url.href.includes(d))) return;

  // Navegação (abrir o app): network-first, fallback pro cache
  if (req.mode === "navigate") {
    e.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put("./index.html", copy));
          return res;
        })
        .catch(() => caches.match("./index.html").then((r) => r || caches.match("./")))
    );
    return;
  }

  // Demais GET (fontes, flatpickr, ícones): cache-first + runtime cache
  e.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req)
        .then((res) => {
          // só cacheia respostas válidas ou opacas (CDN cross-origin)
          if (res && (res.ok || res.type === "opaque")) {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put(req, copy));
          }
          return res;
        })
        .catch(() => cached);
    })
  );
});
