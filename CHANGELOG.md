## [4.5.0 (web)] — 2026-09-20 — ☁️ BACKEND REAL EN PRODUCCIÓN (Cloudflare)

### Infraestructura viva
- **Despliegue Cloudflare completo** (`plataforma-total-web.pages.dev`): Pages + Functions (hybrid SSR), **Workers AI** vinculado y **D1** `plataforma` con esquema aplicado (users / sessions / progreso / certificados).
- **Chat con IA real en producción**: `@cf/meta/llama-3.3-70b-instruct-fp8-fast` (3.1-8b deprecado por CF en 2026) con fallback automático a `llama-3.2-3b-instruct`. Verificado en vivo respondiendo en español.
- **Auth real**: alias+PIN (PBKDF2-SHA256 100k iter, WebCrypto edge) → token sesión 30 días; verificado registro + rechazo de sesión inválida.
- **Progreso en la nube**: GET/POST `/api/progreso` con upsert D1 verificado (save+load round-trip OK).
- **CORS habilitado** en los 3 endpoints (`OPTIONS` 204 preflight verificado desde origen github.io) → la web estática de GitHub Pages consume el backend CF cross-origin.
- **Frontend dual-origin**: `pt.js`/`chat.astro` detectan host `github.io` y apuntan a `https://plataforma-total-web.pages.dev` (fallback same-origin en pages.dev/local).

### Notas
- 100% dentro del free tier de Cloudflare (Pages ilimitado, Workers AI 10k neurons/día, D1 5M reads/día).
- Deploy reproducible: `cd web && ASTRO_BASE=/ npm run build && wrangler pages deploy dist --project-name plataforma-total-web`.

# Changelog

## [4.4.0] - 2026-09-20 (web)
### 🧬 Cumplimiento del SPEC maestro (VISION.md, 82 secciones)
- **`VISION.md`**: documento maestro del producto guardado como fuente de verdad + **`CUMPLIMIENTO.md`**: mapa sección-por-sección (MVP §73 ≈ 90% ✅)
- 💻 **Laboratorio de código** (spec §6/§49): editor + ejecución **Python real en el navegador (Pyodide/WASM, offline tras 1ª carga)** + JavaScript, ejemplos guiados con "error para diagnosticar" (§30), Tab=indent, botón 🤖 "Explicar/Mejorar con IA" que lleva el código al tutor
- 🗺️ **Rutas profesionales** (§19/§35/§67/§66): Full Stack, AI Engineer, Python Pro, Arquitecto — progreso % en vivo y "siguiente misión" por usuario
- 📝 **Evaluación inicial** (§65/§31): 12 preguntas → nivel 0-5 del spec → ruta personalizada +XP; el tutor IA recibe tu nivel
- 🇬🇧 **Inglés técnico** (§33/§34): 41 términos dev con pronunciación 🔊 (TTS) + quiz ES→EN
- 🎚️ **Modos del tutor IA** (§7): Aprendizaje / Asistido / Examen — cambian el system prompt (examen = socrático, sin soluciones) + protocolo "no entiendo" (§37)
## [4.3.0] - 2026-09-18
### 🌐🤖 NUEVA PLATAFORMA WEB (Astro + backend real) — fiel a la app, no una demo
- **Rebuild total de la web con Astro**: sidebar fiel al escritorio, tabs 🏠📚🤖🔥🏆📜💎, tema oscuro customtkinter
- **Tutor IA estilo ChatGPT** (contexto de tu lección actual, chips rápidos, historial) — backend Cloudflare Workers AI gratis
- **Backend real listo**: login alias+PIN (PBKDF2-100k), progreso sincronizado en la nube (D1 SQLite), APIs /api/chat /api/auth /api/progreso + web/DESPLIEGUE.md (10 min, $0)
- **Aprender**: progreso por curso con barras, lecciones leídas ✅, XP por lección/quiz, completado +50 XP
- **Pomodoro** 25/5 con XP y racha · **Progreso** con niveles, emblemas y precisión · **Certificados PNG** con código verificable generados en el navegador
- Frontend estático sirviéndose YA en GitHub Pages (degrada a modo local si el backend aún no se despliega)
- La versión web simplificada anterior se conserva como legacy (`app-legacy-v1.js`, `legacy-index-v1.html`); service worker viejo auto-purgado
## [4.2.0] - 2026-09-18
### 🚚 Mudanza — nuevo repo canónico: SoftEngAi-dev/plataforma-total-pro
- Todo el proyecto (historial completo, releases, web/PWA, marketing) migrado a **github.com/SoftEngAi-dev/plataforma-total-pro**
- La app y la web ahora leen actualizaciones, licencias y `monetizacion.json` desde el nuevo hogar
- Repo anterior queda como histórico (v4.1.0 = última release allí)
## [4.1.0] - 2026-09-18
### 🪟 ¡Ejecutable Windows de doble clic!
- **`PlataformaTotal-Windows.exe`** compilado gratis en GitHub Actions (PyInstaller onefile, icono oficial) — descarga y úsala como cualquier app, sin Python
- Auto-update consciente del formato: si la app corre como `.exe`, descarga y reemplaza el propio ejecutable (rama frozen en `_url_asset` + `_lanzar_reinstalador`)
- GitHub Pages estrena **Web App gratis + PWA instalable** (la `app/` generada en el ciclo anterior se mantiene vigente)
- FIX: paquetes de Release vuelven a llevar carpeta `PlataformaTotal/` interna (formato que espera el auto-instalador)
## [4.0.0] - 2026-09-18
### 💎 Monetización — la app ahora factura
- **Modelo freemium**: 15 cursos de fundamentos GRATIS · 32 cursos PRO (desbloqueo con clave de licencia)
- **Paywall en la app**: gate en cargador de lecciones + guarda en buscador (🔒 en cursos PRO), pantalla de conversión con beneficios, 3 planes y entrada de clave
- **Activación con Lemon Squeezy** (Merchant of Record): validación de clave online una sola vez; tras activar la app sigue 100% offline
- **`monetizacion.json` remoto**: precios y enlaces de checkout editables en el repo sin recompilar (cache 24 h)
- **Sidebar**: badge FREE/PRO + botón "💎 Ser PRO / Activar clave"
- **Landing**: nueva sección #precios (Free / Mensual 7,99 / Anual 79 / Lifetime 169 / packs 24) que lee los enlaces desde monetizacion.json
- **`MONETIZACION.md`**: análisis de mercado completo (Platzi, Codecademy, ZTM, Scrimba, Código Facilito…), justificación de precios, matemática de facturación y plan fase $0 → stores
g — Plataforma Total

Todas las versiones publicadas en: https://github.com/SoftEngAi-dev/plataforma-total-pro/releases

---

## [3.3.0] — 2026-09-18 · 🔄 Auto-actualización desde la app

### Añadido
- 🔄 **La app se actualiza a sí misma**: chequea GitHub Releases al iniciar (silencioso) y con botón "🔄 Buscar actualización" en el sidebar
- ⬇ **Instalación con 1 clic**: descarga la Release correcta para tu SO y se reinstala sola mediante un reinstalador externo (`.bat`/`.sh`) que reemplaza la app al cerrarse y la relanza
- 💻 Modo código fuente: el botón guía con `git pull`
- Indicador de versión v3.3.0 en el sidebar

## [3.2.0] — 2026-09-18 · 🚀 Stack Moderno (Astro & friends)

### Añadido
- 🚀 **Curso de Astro** (5 lecciones): islas, .astro, rutas, Content Collections y despliegue
- 💚 **Curso de Vue 3** (5): SFC, Composition API, Pinia y Nuxt 3
- ▲ **Curso de Next.js** (5): App Router, Server Components, Server Actions, SEO
- 🎨 **Curso de Tailwind CSS** (5): utility-first, responsive, dark:, @theme y shadcn/ui
- 🔥 **Curso de SvelteKit & Svelte 5** (4): runas, +page, form actions, adapters
- 🍞 **Curso de Bun & Deno** (4): los nuevos runtimes, Fresh, Elysia, Hono, edge
- **47 cursos · 269 lecciones · 538 quizzes** · **3.941 archivos** de material de expansión

## [3.1.0] — 2026-09-18 · 🏁 Proyecto Final

### Añadido
- 📖 README con insignias (release, CI, licencia), icono del proyecto y **tabla de descarga directa** con enlaces permanentes `/releases/latest/`
- 🏷️ Topics y homepage configurados en el repositorio de GitHub
- 📜 Este CHANGELOG documentando todo el recorrido
- ©️ Licencia MIT personalizada

## [3.0.3] — 2026-09-18 · 🎨 Icono oficial

### Añadido
- 🖼️ Icono oficial de la app (birrete de graduación + llaves de código `{ }`): `.ico` multi-tamaño (Windows), `.icns` (macOS) y PNG 16–512 px
- Icono **incrustado en los 3 ejecutables** (`--icon` en PyInstaller) y en la **ventana/barra de tareas** de la app (`iconphoto` con PNG empaquetado vía `--add-data`)
- Scripts de build locales actualizados con icono

## [3.0.1 → 3.0.2] — 2026-09-18 · 🔧 CI/CD

### Corregido
- El workflow ahora se dispara también con **tags `v*`** → Release automática con los 3 ejecutables adjuntos (descargas permanentes, sin caducidad)
- `actions/checkout` añadido al job de Release (`gh` necesita un repo git)

## [3.0.0] — 2026-09-18 · 🚀 Reconstrucción total

### Añadido
- 🎓 App completa: **41 cursos · 241 lecciones · 482 quizzes** (100% cobertura, validado por test)
- Buscador global 🔍 · Quizzes con IA 🤖 · Pomodoro 🍅 · Racha 🔥 · Certificados SHA-256 🎓 · Chat IA con memoria SQLite · Recomendador 🧭
- 🌱 3.601 archivos de material de estudio (`expansion/`): flashcards, ejercicios, cheatsheets, roadmaps, retos diarios, entrevistas…
- 🖥️ Ejecutable Linux compilado + workflow CI que compila **Windows/macOS/Linux** en la nube
- 🚀 Scripts guiados de subida a GitHub (PowerShell + bash) y guía paso a paso
