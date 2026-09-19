# 🚀 DESPLIEGUE DEL BACKEND — Plataforma Total WEB (Cloudflare, gratis para siempre)
### 10 minutos, U$S 0 — tutor IA + login + progreso en la nube activados

> **Hoy ya funciona todo el FRONTEND** en GitHub Pages (cursos, quizzes, pomo, certificados, progreso local).
> Este documento enciende el **BACKEND**: chat con IA real, login alias+PIN y sincronización entre dispositivos.
> Stack: **Cloudflare Pages + Workers + D1 (SQLite) + Workers AI** — todo en tier gratis.

---

## 🧭 Arquitectura

```
Navegador → https://plataforma-total-web.pages.dev      (Cloudflare Pages, ¡gratis!)
  ├─ páginas estáticas (Astro)     → las mismas que GitHub Pages sirve hoy
  ├─ /api/chat      → Workers AI   → @cf/meta/llama-3.1-8b-instruct (gratis: 10K neuronas/día)
  ├─ /api/auth      → D1 users+sessions (PBKDF2, WebCrypto nativo)
  └─ /api/progreso  → D1 progreso (XP/racha/lecciones por usuario)
```

Plan gratis de Cloudflare (límites reales, sobrados para empezar): 100.000 requests/día · D1 5M lecturas/día · AI 10K neuronas/día.

---

## ✅ Pasos (los corrés UNA vez)

```bash
cd web
npm install                       # si no está hecho
npx wrangler login                # abre el navegador → creás cuenta Cloudflare GRATIS (email y listo)

# 1) Crear la base D1 y aplicar el esquema
npx wrangler d1 create plataforma
#   → copiar el "database_id" que imprime y pegarlo en wrangler.toml (línea database_id)
npx wrangler d1 execute plataforma --file=schema.sql

# 2) Build para Cloudflare (base raíz) y deploy
ASTRO_BASE=/ npm run build
npm run deploy                    # = wrangler pages deploy dist
```

Listo: tu backend queda en `https://plataforma-total-web.pages.dev` con API funcional.
(CF te activa Workers AI automáticamente al primer request que usa el binding `[ai]`).

## 🤖 Opción B: que yo lo despliegue por vos

Como hicimos con GitHub: creás la cuenta Cloudflare gratis (2 min, sin tarjeta, sin KYC) → en `dash.cloudflare.com → My Profile → API Tokens → Create Token` (template "Edit Cloudflare Workers") → me pasás **token + Account ID** → yo corro todos los comandos y te devuelvo la URL live. (El token es revocable en 1 clic; nunca compartas contraseñas ni datos bancarios.)

## 🎛️ Verificar que funciona

```bash
curl https://plataforma-total-web.pages.dev/api/progreso
# → {"ok":false,"error":"sesión inválida"}  ✅ (significa: API viva, pidiendo token)
curl -X POST https://plataforma-total-web.pages.dev/api/chat \
  -H 'Content-Type: application/json' -d '{"messages":[{"role":"user","content":"hola"}]}'
# → {"respuesta":"..."}  ✅ tutor respondiendo
```

## 🔄 Actualizaciones futuras

Editás `web/src/...` → `ASTRO_BASE=/ npm run build && npm run deploy` para el backend, y
`npm run build && cp -r dist/plataforma-total-pro/app/. ../docs/app/` + push para el frontend estático.

## 🛡️ Notas de seguridad implementadas

- PIN hasheado con **PBKDF2-SHA256, 100.000 iteraciones, salt por usuario** (nunca se guarda en claro)
- Sesiones con token aleatorio 48 hex, expiran a 30 días
- Límite de tamaño de progreso (200 KB) y longitud de mensajes del chat
- Sin cookies de terceros, sin trackers — la sesión vive en tu `localStorage`
