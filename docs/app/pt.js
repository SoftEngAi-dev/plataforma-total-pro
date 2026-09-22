/* 🧠 PT — estado local + sincronización cloud (alias+PIN → Workers/D1) */
(function () {
  const K = 'pt_web_v1';
  const DEF = () => ({
    alias: null, token: null,
    xp: 0, quiz_ok: 0, quiz_tot: 0,
    racha: { n: 0, ultimo: null },           // último día ISO con actividad
    leidas: {},                               // {idxCurso: [idxLeccion,...]}
    ultima: null,                             // {c, j, t}
    completados: [],                          // slugs de cursos terminados
    certs: [],                                // {codigo, curso, fecha}
  });
  const PT = {
    s: DEF(),
    cargar() { try { this.s = { ...DEF(), ...JSON.parse(localStorage.getItem(K) || '{}') }; } catch (e) {} },
    guardar() { localStorage.setItem(K, JSON.stringify(this.s)); this.syncPush(); },
    hoy() { return new Date().toISOString().slice(0, 10); },

    nivel() { return Math.floor(Math.sqrt(this.s.xp / 50)) + 1; },  // curva suave
    xpNivel() { const n = this.nivel(), base = 50 * (n - 1) ** 2, sig = 50 * n ** 2;
      return { enNivel: this.s.xp - base, total: sig - base, pct: Math.min(100, 100 * (this.s.xp - base) / (sig - base)) }; },

    actividad(xp) {
      const h = this.hoy();
      if (this.s.racha.ultimo !== h) {
        const ayer = new Date(Date.now() - 864e5).toISOString().slice(0, 10);
        this.s.racha.n = (this.s.racha.ultimo === ayer) ? this.s.racha.n + 1 : 1;
        this.s.racha.ultimo = h;
      }
      this.s.xp += xp;
      this.guardar();
    },

    marcarLeida(ci, j, titulo) {
      this.s.leidas[ci] = this.s.leidas[ci] || [];
      if (!this.s.leidas[ci].includes(j)) { this.s.leidas[ci].push(j); this.actividad(10); }
      this.s.ultima = { c: ci, j, t: titulo };
      this.guardar();
    },

    /* ── sesión / nube ── */
    apiBase() {  // si estamos en GitHub Pages, el backend vive en Cloudflare
      return location.hostname.endsWith('github.io') ? 'https://plataforma-total-web.pages.dev/' : '';
    },
    api(path, opts) {
      const h = { 'Content-Type': 'application/json' };
      if (this.s.token) h['X-Token'] = this.s.token;
      return fetch(this.apiBase() + 'api/' + path, { ...opts, headers: h }).then(r => r.json());
    },
    nubeOn: false,
    syncPush() {
      if (!this.s.token) return;
      this.api('progreso', { method: 'POST', body: JSON.stringify({ data: this.s }) })
        .then(d => { this.nubeOn = !!d.ok; this.pintarNube(); }).catch(() => {});
    },
    syncPull() {
      if (!this.s.token) return Promise.resolve();
      return this.api('progreso').then(d => {
        if (d.ok && d.data && (d.data.xp || 0) > this.s.xp) {
          const keepTok = { alias: this.s.alias, token: this.s.token };
          this.s = { ...DEF(), ...d.data, ...keepTok };
          localStorage.setItem(K, JSON.stringify(this.s));
        }
        this.nubeOn = !!d.ok; this.pintarNube();
      }).catch(() => {});
    },
    login(alias, pin) {
      return this.api('auth', { method: 'POST', body: JSON.stringify({ alias, pin }) })
        .then(d => {
          if (!d.ok) return d;
          this.s.alias = d.alias; this.s.token = d.token; this.guardar();
          return this.syncPull().then(() => this.proSinc()).then(() => d);
        });
    },
    logout() { this.s.alias = this.s.token = null; this.s.leidas = {}; this.guardar(); location.reload(); },
    /* ── 💎 PRO (Lemon Squeezy vía /api/pro) ── */
    esPro() { return !!this.s.pro; },
    proSinc() {  // consulta al backend si esta sesión es PRO (auto al loguear)
      if (!this.s.token) return Promise.resolve(false);
      return this.api('pro').then(d => {
        if (d.ok) { this.s.pro = !!d.pro; this.guardar(); }
        return this.s.pro;
      }).catch(() => false);
    },
    proActivar(email) {  // vincula el email de compra con esta sesión
      if (!this.s.token) return Promise.resolve({ ok: false, error: 'Iniciá sesión primero (sidebar)' });
      return this.api('pro', { method: 'POST', body: JSON.stringify({ email }) }).then(d => {
        if (d.ok && d.pro) { this.s.pro = true; this.guardar(); }
        return d;
      }).catch(() => ({ ok: false, error: 'Error de red' }));
    },
    pintarNube() {
      const el = document.getElementById('estado-nube'); if (!el) return;
      el.textContent = this.s.token ? (this.nubeOn ? 'nube: sincronizado ✅' : 'nube: sin backend (local)') : 'nube: desconectado';
    },
    initSesionUI() {
      this.cargar();
      const est = document.getElementById('estado-sesion');
      const box = document.getElementById('loginbox');
      if (est) {
        if (this.s.alias) {
          est.innerHTML = `👤 <b>${PT.esc(this.s.alias)}</b> · <a href="#" id="lnk-login">salir</a>`;
          est.querySelector('#lnk-login').onclick = e => { e.preventDefault(); this.logout(); };
        } else if (document.getElementById('lnk-login')) {
          document.getElementById('lnk-login').onclick = e => { e.preventDefault(); box.hidden = !box.hidden; };
        }
      }
      const btn = document.getElementById('btn-login');
      if (btn) btn.onclick = () => {
        const a = document.getElementById('lg-alias').value.trim();
        const p = document.getElementById('lg-pin').value.trim();
        const msg = document.getElementById('lg-msg');
        if (!a || p.length < 4) { msg.textContent = '⚠ alias y PIN de 4+ dígitos'; return; }
        msg.textContent = '⏳ …';
        this.login(a, p).then(d => {
          if (d && d.ok) { msg.textContent = '✅ ¡Hola ' + PT.esc(d.alias) + '! Sincronizando…'; setTimeout(() => location.reload(), 600); }
          else msg.textContent = '⚠ ' + (d && d.error ? d.error : 'sin backend desplegado (modo local)');
        }).catch(() => { msg.textContent = '⚠ sin backend desplegado (modo local)'; });
      };
      this.syncPull();
    },
    esc(s) { return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); },
  };
  window.PT = PT;
})();
