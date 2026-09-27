/* Plataforma Total v5 — estado local, API unificada y sincronización */
(function () {
  'use strict';
  const K = 'pt_web_v3';
  const OLD_KEYS = ['pt_web_v2', 'pt_web_v1'];
  const IDB_NAME = 'PlataformaTotal';
  const IDB_STORE = 'state';
  const DEVICE_KEY = 'pt_device_id';

  const DEF = () => ({
    alias: null,
    token: null,
    pro: false,
    xp: 0,
    quiz_ok: 0,
    quiz_tot: 0,
    racha: { n: 0, ultimo: null },
    dias_activos: [],
    leidas: {},
    quiz_lessons: {},
    ultima: null,
    completados: [],
    certs: [],
    evaluacion: null,
    device_id: null,
    updated_at: null,
  });

  const PT = {
    s: DEF(),
    nubeOn: false,
    backendOk: null,
    backendInfo: null,
    _idbReady: null,
    _loadPromise: null,
    _syncing: false,

    _uuid() {
      if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID();
      return 'pt-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2);
    },

    _deviceId() {
      let id = null;
      try { id = localStorage.getItem(DEVICE_KEY); } catch (_) {}
      if (!id) {
        id = this._uuid();
        try { localStorage.setItem(DEVICE_KEY, id); } catch (_) {}
      }
      return id;
    },

    _idbOpen() {
      if (!('indexedDB' in window)) return Promise.resolve(null);
      if (this._idbReady) return this._idbReady;
      this._idbReady = new Promise(resolve => {
        const req = indexedDB.open(IDB_NAME, 1);
        req.onupgradeneeded = () => {
          if (!req.result.objectStoreNames.contains(IDB_STORE)) req.result.createObjectStore(IDB_STORE);
        };
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => resolve(null);
      });
      return this._idbReady;
    },

    async _idbGet() {
      const db = await this._idbOpen();
      if (!db) return null;
      return new Promise(resolve => {
        const q = db.transaction(IDB_STORE, 'readonly').objectStore(IDB_STORE).get('profile');
        q.onsuccess = () => resolve(q.result || null);
        q.onerror = () => resolve(null);
      });
    },

    async _idbPut(v) {
      const db = await this._idbOpen();
      if (!db) return;
      await new Promise(resolve => {
        const tx = db.transaction(IDB_STORE, 'readwrite');
        tx.objectStore(IDB_STORE).put(v, 'profile');
        tx.oncomplete = () => resolve();
        tx.onerror = () => resolve();
        tx.onabort = () => resolve();
      });
    },

    _merge(a, b) {
      a = a || {};
      b = b || {};
      const leidas = { ...(a.leidas || {}) };
      for (const [k, v] of Object.entries(b.leidas || {})) {
        leidas[k] = Array.from(new Set([...(leidas[k] || []), ...(v || [])])).sort((x, y) => Number(x) - Number(y));
      }
      const dias = Array.from(new Set([...(a.dias_activos || []), ...(b.dias_activos || [])])).sort();
      const completados = Array.from(new Set([...(a.completados || []), ...(b.completados || [])]));
      const quiz = { ...(a.quiz_lessons || {}) };
      for (const [k, v] of Object.entries(b.quiz_lessons || {})) {
        const av = quiz[k];
        if (!av) {
          quiz[k] = { ...v };
          continue;
        }
        quiz[k] = {
          correct: Math.max(Number(av.correct || 0), Number(v.correct || 0)),
          answered: Math.max(Number(av.answered || 0), Number(v.answered || 0)),
          total: Math.max(Number(av.total || 0), Number(v.total || 0)),
          updated_at: [av.updated_at, v.updated_at].filter(Boolean).sort().pop() || null,
        };
      }
      const ultima = [a.ultima, b.ultima].filter(Boolean).sort((x, y) => Number(y.at || 0) - Number(x.at || 0))[0] || null;
      const out = {
        ...DEF(),
        ...a,
        ...b,
        leidas,
        dias_activos: dias,
        completados,
        quiz_lessons: quiz,
        xp: Math.max(Number(a.xp || 0), Number(b.xp || 0)),
        racha: {
          n: Math.max(Number(a.racha && a.racha.n || 0), Number(b.racha && b.racha.n || 0)),
          ultimo: a.racha && a.racha.ultimo || b.racha && b.racha.ultimo || null,
        },
        ultima,
        updated_at: [a.updated_at, b.updated_at].filter(Boolean).sort().pop() || null,
      };
      out.quiz_ok = Object.values(quiz).filter(x => Number(x.correct || 0) >= Number(x.total || 0) && Number(x.total || 0) > 0).length;
      out.quiz_tot = Object.keys(quiz).length;
      return out;
    },

    _recalcularQuizzes() {
      const q = this.s.quiz_lessons || {};
      this.s.quiz_tot = Object.keys(q).length;
      this.s.quiz_ok = Object.values(q).filter(x => Number(x.correct || 0) >= Number(x.total || 0) && Number(x.total || 0) > 0).length;
    },

    cargar() {
      if (this._loadPromise) return this.s;
      let raw = {};
      try {
        raw = JSON.parse(localStorage.getItem(K) || '{}');
        if (!Object.keys(raw).length) {
          for (const key of OLD_KEYS) {
            const old = localStorage.getItem(key);
            if (old) {
              raw = JSON.parse(old);
              break;
            }
          }
        }
      } catch (_) {}
      this.s = { ...DEF(), ...raw };
      this.s.device_id = this.s.device_id || this._deviceId();
      this.s.updated_at = this.s.updated_at || new Date().toISOString();
      this._recalcularQuizzes();
      this._loadPromise = this._idbGet().then(v => {
        if (v) {
          const merged = this._merge(this.s, v);
          merged.alias = this.s.alias || v.alias || null;
          merged.token = this.s.token || v.token || null;
          merged.pro = !!(this.s.pro || v.pro);
          this.s = merged;
          this._persistOnly();
        }
        return this.s;
      }).catch(() => this.s);
      return this.s;
    },

    ready() {
      this.cargar();
      return this._loadPromise || Promise.resolve(this.s);
    },

    _persistOnly() {
      this.s.device_id = this.s.device_id || this._deviceId();
      this.s.updated_at = new Date().toISOString();
      this._recalcularQuizzes();
      try { localStorage.setItem(K, JSON.stringify(this.s)); } catch (_) {}
      this._idbPut(this.s).catch(() => {});
    },

    guardar() {
      this._persistOnly();
      this.syncPush();
    },

    hoy() {
      const d = new Date();
      return [d.getFullYear(), String(d.getMonth() + 1).padStart(2, '0'), String(d.getDate()).padStart(2, '0')].join('-');
    },

    nivel() {
      return Math.floor(Math.sqrt(Math.max(0, Number(this.s.xp || 0)) / 50)) + 1;
    },

    xpNivel() {
      const n = this.nivel();
      const base = 50 * (n - 1) ** 2;
      const sig = 50 * n ** 2;
      return { enNivel: this.s.xp - base, total: sig - base, pct: Math.min(100, Math.max(0, 100 * (this.s.xp - base) / Math.max(1, sig - base))) };
    },

    actividad(xp) {
      const h = this.hoy();
      const dias = new Set(this.s.dias_activos || []);
      dias.add(h);
      this.s.dias_activos = Array.from(dias).sort();
      if (this.s.racha.ultimo !== h) {
        const ayerDate = new Date();
        ayerDate.setDate(ayerDate.getDate() - 1);
        const a = [ayerDate.getFullYear(), String(ayerDate.getMonth() + 1).padStart(2, '0'), String(ayerDate.getDate()).padStart(2, '0')].join('-');
        this.s.racha.n = this.s.racha.ultimo === a ? Number(this.s.racha.n || 0) + 1 : 1;
        this.s.racha.ultimo = h;
      }
      this.s.xp = Math.max(0, Number(this.s.xp || 0) + Number(xp || 0));
      this.guardar();
    },

    marcarLeida(ci, j, titulo) {
      this.s.leidas[ci] = this.s.leidas[ci] || [];
      if (!this.s.leidas[ci].includes(j)) {
        this.s.leidas[ci].push(j);
        this.s.leidas[ci].sort((a, b) => a - b);
        this.actividad(10);
      }
      this.s.ultima = { c: ci, j, t: titulo, at: Date.now() };
      this.guardar();
    },

    registrarQuiz(ci, j, correct, answered, total) {
      const key = String(ci) + ':' + String(j);
      const old = this.s.quiz_lessons[key] || {};
      this.s.quiz_lessons[key] = {
        correct: Math.max(Number(old.correct || 0), Number(correct || 0)),
        answered: Math.max(Number(old.answered || 0), Number(answered || 0)),
        total: Math.max(Number(old.total || 0), Number(total || 0)),
        updated_at: new Date().toISOString(),
      };
      this._recalcularQuizzes();
      this._persistOnly();
      this.syncPush();
    },

    cursoQuizStats(ci, lecciones) {
      let total = 0, ok = 0;
      (lecciones || []).forEach((l, j) => {
        if (!l.q || !l.q.length) return;
        total++;
        const q = this.s.quiz_lessons[String(ci) + ':' + String(j)];
        if (q && Number(q.correct || 0) >= Number(q.total || 0) && Number(q.total || 0) >= l.q.length) ok++;
      });
      return { ok, total };
    },

    completarCurso(ci, slug, lecciones) {
      const qs = this.cursoQuizStats(ci, lecciones);
      const listas = (this.s.leidas[ci] || []).length >= (lecciones || []).length;
      const completo = listas && qs.ok === qs.total;
      if (completo && slug && !this.s.completados.includes(slug)) {
        this.s.completados.push(slug);
        this.actividad(50);
      } else {
        this.guardar();
      }
      return completo;
    },

    async data(path) {
      const clean = String(path || '').replace(/^\\/+/, '');
      const isIndex = clean === 'data/indice.json';
      const isCourse = clean.startsWith('data/cursos/') && clean.endsWith('.json');
      if (isIndex || isCourse) {
        try {
          const endpoint = isIndex ? 'catalog' : 'course?slug=' + encodeURIComponent(clean.slice('data/cursos/'.length, -5));
          const d = await this.api(endpoint);
          if (d && d.ok && d.data) return d.data;
        } catch (_) {}
      }
      const base = (typeof location !== 'undefined' && location.pathname.indexOf('/plataforma-total-pro/app/') === 0) ? '/plataforma-total-pro/app/' : '/';
      const r = await fetch(base + clean, { cache: 'no-store' });
      if (!r.ok) throw new Error('No se pudo cargar ' + clean);
      return r.json();
    },

    apiBase() {
      if (typeof location === 'undefined') return '';
      if (location.hostname === 'localhost' || location.hostname === '127.0.0.1') return '/';
      if (location.hostname.endsWith('github.io')) return 'https://plataforma-total-web.pages.dev/';
      return '/';
    },

    _fetch(url, opts) {
      const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
      const timer = controller ? setTimeout(() => controller.abort(), 12000) : null;
      const headers = { 'Accept': 'application/json', 'Content-Type': 'application/json', ...(opts && opts.headers || {}) };
      if (this.s.token) headers['X-Token'] = this.s.token;
      return fetch(this.apiBase() + url, { ...(opts || {}), headers, cache: 'no-store', signal: controller && controller.signal })
        .then(async r => {
          const text = await r.text();
          let d = {};
          try { d = text ? JSON.parse(text) : {}; } catch (_) { d = { ok: false, error: text.slice(0, 180) }; }
          if (!r.ok && !d.error) d.error = 'HTTP ' + r.status;
          return d;
        })
        .finally(() => { if (timer) clearTimeout(timer); });
    },

    api(path, opts) {
      return this._fetch('api/' + path, opts);
    },

    health() {
      return this.api('health').then(d => {
        this.backendOk = !!d.ok;
        this.backendInfo = d;
        this.pintarNube();
        return d;
      }).catch(() => {
        this.backendOk = false;
        this.pintarNube();
        return { ok: false };
      });
    },

    _isLocalRuntime() {
      return location.hostname === 'localhost' || location.hostname === '127.0.0.1';
    },

    syncPush() {
      if (this._syncing) return;
      const local = this._isLocalRuntime();
      if (!this.s.token && !local) return;
      this._syncing = true;
      this.api('progreso', {
        method: 'POST',
        body: JSON.stringify({ data: this.s }),
      }).then(d => {
        this.nubeOn = !!d.ok;
        if (d.ok && d.data) {
          const keep = { alias: this.s.alias, token: this.s.token, pro: this.s.pro };
          this.s = { ...this._merge(this.s, d.data), ...keep };
          this._persistOnly();
        }
        this.pintarNube();
      }).catch(() => {}).finally(() => { this._syncing = false; });
    },

    syncPull() {
      const local = this._isLocalRuntime();
      if (!this.s.token && !local) return Promise.resolve();
      return this.api('progreso').then(d => {
        if (d.ok && d.data) {
          const keep = { alias: this.s.alias, token: this.s.token, pro: this.s.pro };
          this.s = { ...this._merge(this.s, d.data), ...keep };
          this._persistOnly();
        }
        this.nubeOn = !!d.ok;
        this.pintarNube();
        return d;
      }).catch(() => {
        this.nubeOn = false;
        this.pintarNube();
        return { ok: false };
      });
    },

    login(alias, pin) {
      return this.api('auth', { method: 'POST', body: JSON.stringify({ alias, pin }) })
        .then(d => {
          if (!d.ok) return d;
          this.s.alias = d.alias;
          this.s.token = d.token;
          this.guardar();
          return this.syncPull().then(() => this.proSinc()).then(() => d);
        });
    },

    logout() {
      const localState = this._merge(this.s, {});
      this.s = { ...DEF(), ...localState, alias: null, token: null, pro: false };
      this._persistOnly();
      location.reload();
    },

    esPro() {
      return !!this.s.pro;
    },

    proSinc() {
      if (!this.s.token) return Promise.resolve(!!this.s.pro);
      return this.api('pro').then(d => {
        if (d.ok) {
          this.s.pro = !!d.pro;
          this._persistOnly();
        }
        return !!this.s.pro;
      }).catch(() => !!this.s.pro);
    },

    proActivar(email) {
      if (!this.s.token) return Promise.resolve({ ok: false, error: 'Iniciá sesión primero.' });
      return this.api('pro', { method: 'POST', body: JSON.stringify({ email: email }) })
        .then(d => {
          if (d.ok && d.pro) {
            this.s.pro = true;
            this.guardar();
          }
          return d;
        })
        .catch(() => ({ ok: false, error: 'Error de conexión.' }));
    },

    pintarNube() {
      const el = document.getElementById('estado-nube');
      if (!el) return;
      if (this._isLocalRuntime()) {
        el.textContent = this.backendOk === true ? 'local: conectado ✅' : this.backendOk === false ? 'local: sin API' : 'local: comprobando…';
        return;
      }
      if (this.s.token) el.textContent = this.nubeOn ? 'nube: sincronizado ✅' : (this.backendOk === false ? 'nube: sin backend' : 'nube: conectando…');
      else el.textContent = this.backendOk === true ? 'backend online · sesión local' : 'nube: desconectado';
    },

    initSesionUI() {
      this.cargar();
      const est = document.getElementById('estado-sesion');
      const box = document.getElementById('loginbox');
      if (est) {
        if (this.s.alias) {
          est.innerHTML = '👤 <b>' + this.esc(this.s.alias) + '</b> · <a href="#" id="lnk-login">salir</a>';
          est.querySelector('#lnk-login').onclick = e => { e.preventDefault(); this.logout(); };
        } else if (document.getElementById('lnk-login') && box) {
          document.getElementById('lnk-login').onclick = e => { e.preventDefault(); box.hidden = !box.hidden; };
        }
      }
      const btn = document.getElementById('btn-login');
      if (btn) btn.onclick = () => {
        const a = document.getElementById('lg-alias').value.trim();
        const p = document.getElementById('lg-pin').value.trim();
        const msg = document.getElementById('lg-msg');
        if (!a || p.length < 4) { msg.textContent = '⚠ alias y PIN de 4+ caracteres'; return; }
        msg.textContent = '⏳ conectando…';
        this.login(a, p).then(d => {
          if (d && d.ok) {
            msg.textContent = '✅ ' + this.esc(d.alias) + ' · nube conectada';
            setTimeout(() => location.reload(), 500);
          } else {
            msg.textContent = '⚠ ' + (d && d.error ? d.error : 'No se pudo iniciar sesión');
          }
        }).catch(() => { msg.textContent = '⚠ Error de conexión'; });
      };
      this.health();
      this.syncPull();
    },

    esc(s) {
      return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    },
  };

  window.PT = PT;
})();
