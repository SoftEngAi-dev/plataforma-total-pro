/* 🧠 PT — estado local + sincronización cloud (alias+PIN → Workers/D1) */
(function () {
  const K = 'pt_web_v2';
  const IDB_NAME = 'PlataformaTotal';
  const IDB_STORE = 'state';
  const DEVICE_KEY = 'pt_device_id';
  const DEF = () => ({
    alias: null, token: null,
    xp: 0, quiz_ok: 0, quiz_tot: 0,
    racha: { n: 0, ultimo: null },           // último día ISO con actividad
    leidas: {},                               // {idxCurso: [idxLeccion,...]}
    ultima: null,                             // {c, j, t}
    completados: [],                          // slugs de cursos terminados
    certs: [],                                // {codigo, curso, fecha}
    device_id: null,
    updated_at: null,
  });
  const PT = {
    s: DEF(),
    _idbReady: null,
    _syncing: false,
    _uuid() { return crypto?.randomUUID ? crypto.randomUUID() : 'pt-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2); },
    _deviceId() { let id=null; try{id=localStorage.getItem(DEVICE_KEY);}catch{} if(!id){id=this._uuid();try{localStorage.setItem(DEVICE_KEY,id);}catch{}} return id; },
    _idbOpen() {
      if (!('indexedDB' in window)) return Promise.resolve(null);
      if (this._idbReady) return this._idbReady;
      this._idbReady = new Promise(resolve => {
        const r=indexedDB.open(IDB_NAME,1);
        r.onupgradeneeded=()=>{if(!r.result.objectStoreNames.contains(IDB_STORE))r.result.createObjectStore(IDB_STORE);};
        r.onsuccess=()=>resolve(r.result); r.onerror=()=>resolve(null);
      }); return this._idbReady;
    },
    async _idbGet(){const db=await this._idbOpen();if(!db)return null;return new Promise(resolve=>{const q=db.transaction(IDB_STORE,'readonly').objectStore(IDB_STORE).get('profile');q.onsuccess=()=>resolve(q.result||null);q.onerror=()=>resolve(null);});},
    async _idbPut(v){const db=await this._idbOpen();if(!db)return;await new Promise(resolve=>{const tx=db.transaction(IDB_STORE,'readwrite');tx.objectStore(IDB_STORE).put(v,'profile');tx.oncomplete=()=>resolve();tx.onerror=()=>resolve();tx.onabort=()=>resolve();});},
    _merge(a,b){
      a=a||{};b=b||{};const leidas={...(a.leidas||{})};
      for(const [k,v] of Object.entries(b.leidas||{}))leidas[k]=Array.from(new Set([...(leidas[k]||[]),...(v||[])])).sort((x,y)=>x-y);
      const ultima=[a.ultima,b.ultima].filter(Boolean).sort((x,y)=>Number(y.at||0)-Number(x.at||0))[0]||a.ultima||b.ultima||null;
      return {...DEF(),...a,...b,leidas,completados:Array.from(new Set([...(a.completados||[]),...(b.completados||[])])),
        xp:Math.max(Number(a.xp||0),Number(b.xp||0)),quiz_ok:Math.max(Number(a.quiz_ok||0),Number(b.quiz_ok||0)),quiz_tot:Math.max(Number(a.quiz_tot||0),Number(b.quiz_tot||0)),
        racha:{n:Math.max(Number(a.racha?.n||0),Number(b.racha?.n||0)),ultimo:a.racha?.ultimo||b.racha?.ultimo||null},ultima};
    },
    cargar(){
      try{this.s={...DEF(),...JSON.parse(localStorage.getItem(K)||'{}')};}catch{this.s=DEF();}
      this.s.device_id=this.s.device_id||this._deviceId();this.s.updated_at=this.s.updated_at||new Date().toISOString();
      this._idbGet().then(v=>{if(!v)return;const m=this._merge(this.s,v);m.alias=this.s.alias||v.alias||null;m.token=this.s.token||v.token||null;this.s={...DEF(),...m};try{localStorage.setItem(K,JSON.stringify(this.s));}catch{}}).catch(()=>{});
      return this.s;
    },
    guardar(){
      this.s.device_id=this.s.device_id||this._deviceId();this.s.updated_at=new Date().toISOString();
      try{localStorage.setItem(K,JSON.stringify(this.s));}catch{} this._idbPut(this.s).catch(()=>{}); this.syncPush();
    },
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
      this.s.ultima = { c: ci, j, t: titulo, at: Date.now() };
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
    syncPush(){
      if(!this.s.token||this._syncing)return;this._syncing=true;
      this.api('progreso',{method:'POST',body:JSON.stringify({data:this.s})}).then(d=>{
        this.nubeOn=!!d.ok;
        if(d.ok&&d.data){const k={alias:this.s.alias,token:this.s.token};this.s={...this._merge(this.s,d.data),...k};try{localStorage.setItem(K,JSON.stringify(this.s));}catch{};this._idbPut(this.s).catch(()=>{});}
        this.pintarNube();
      }).catch(()=>{}).finally(()=>{this._syncing=false;});
    },
    syncPull(){if(!this.s.token)return Promise.resolve();return this.api('progreso').then(d=>{if(d.ok&&d.data){const k={alias:this.s.alias,token:this.s.token};this.s={...this._merge(this.s,d.data),...k};try{localStorage.setItem(K,JSON.stringify(this.s));}catch{};this._idbPut(this.s).catch(()=>{});}this.nubeOn=!!d.ok;this.pintarNube();}).catch(()=>{});},
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
