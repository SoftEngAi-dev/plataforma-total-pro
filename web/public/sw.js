/* 📦 Service Worker — PWA Plataforma Total (offline-first del contenido propio)
   Estrategia: shell + currícula precache · páginas network-first · assets stale-while-revalidate
   · /api/* siempre red (nunca cachear datos personales) */
const V = 'pt-v4.9.1';
const B = self.registration.scope;            // funciona en / y en /plataforma-total-pro/app/
const NUCLEO = ['', 'pt.js', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png',
                'data/indice.json', 'data/corpus.json', 'tutor.js'];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(V).then(c => c.addAll(NUCLEO.map(p => B + p))).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET') return;                    // POST/OPTIONS → red pura
  if (url.pathname.includes('/api/')) return;                // datos personales → NUNCA cache

  // navegaciones: red primero, caché si cae (modo offline real)
  if (e.request.mode === 'navigate') {
    e.respondWith(
      fetch(e.request)
        .then(r => { const copia = r.clone(); caches.open(V).then(c => c.put(e.request, copia)); return r; })
        .catch(() => caches.match(e.request).then(r => r || caches.match(B)))
    );
    return;
  }

  // resto (estáticos + cursos JSON, se cachean al vuelo): stale-while-revalidate
  e.respondWith(
    caches.match(e.request).then(cacheado => {
      const fresca = fetch(e.request).then(r => {
        if (r.ok && url.origin === location.origin) {
          const copia = r.clone();
          caches.open(V).then(c => c.put(e.request, copia));
        }
        return r;
      }).catch(() => cacheado);
      return cacheado || fresca;
    })
  );
});
