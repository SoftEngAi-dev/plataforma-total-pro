// Migración v4.3.0: limpia caches de la versión anterior y se auto-desregistra.
self.addEventListener('install', e => self.skipWaiting());
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(ks => Promise.all(ks.map(k => caches.delete(k))))
      .then(() => self.registration.unregister())
      .then(() => self.clients.matchAll()).then(cs => cs.forEach(c => c.navigate(c.url)))
  );
});
