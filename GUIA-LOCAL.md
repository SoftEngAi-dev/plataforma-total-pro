# 🖥️ Plataforma Total — Guía de instalación LOCAL (Windows)

**Versión del kit: desktop v4.5.0 · 57 cursos (17 gratis + 40 PRO) · 329 lecciones · 658 quizzes**
La app es **100% offline-first**: funciona completa sin internet (contenido, tutor de estudio, quizzes, certificados locales). Internet solo se usa para: sincronizar tu progreso con tu cuenta web, activar licencias PRO y el Tutor IA (nube u Ollama local).

---

## ⚡ Opción 1 — Instalador (recomendada, 2 minutos)

1. Ejecutá **`PlataformaTotal-Windows.exe`**.
2. Si Windows SmartScreen avisa *"Windows protegió su PC"* (normal: el instalador no tiene certificado de firma pago — U$S 0 es U$S 0 😄):
   → clic en **"Más información"** → **"Ejecutar de todas formas"**.
3. Seguí el asistente → se crea acceso directo en el escritorio y menú inicio.
4. Abrir **Plataforma Total** → ✅ **57 cursos disponibles de inmediato**, *Sin miedo a romper*.

### Prueba de fuego (30 segundos)
- Abrí el curso **📐 Matemáticas para Programadores** (gratis) → lección 1 (binario/máscaras).
- Resolvé su quiz → tu progreso queda guardado localmente (SQLite en tu PC).
- Generá un **certificado** de prueba → se guarda en tu carpeta de documentos.

---

## 💎 Opción 2 — PRO en local

- **17 cursos gratis** abiertos siempre (índices: Python, HTML, CSS, Git, redes, Matemáticas, Lógica, etc.).
- **40 cursos PRO** se desbloquean con una clave de licencia (Lemon Squeezy, cuando el riel global esté activo) o vía sync con tu cuenta web PRO (riel regional Mercado Pago ya operativo en la web).
- Menú **💎 Ser PRO** → pegar clave → queda guardado en `licencia.json` (carpeta de datos de la app).

---

## 🤖 Opcional — Tutor IA 100% local (privado, gratis)

La app detecta automáticamente [Ollama](https://ollama.com) si está corriendo (`localhost:11434`):

```powershell
winget install Ollama.Ollama
ollama pull llama3.2:3b   # ~2 GB, baja una vez y queda local
```

Con esto el Tutor IA (resúmenes, quizzes generados, chat de estudio) funciona **en tu PC, sin nube ni costo**. Sin Ollama, la app usa su tutor propio de reglas (offline igual).

---

## 🧑‍💻 Opción 3 — Correr desde el código fuente (si querés modificarla)

```powershell
git clone https://github.com/SoftEngAi-dev/plataforma-total-pro.git
cd plataforma-total-pro
pip install -r requirements.txt
python main.py
```

(o doble clic en `run.bat`)

---

## 🌐 La app también vive en la nube (ya publicada)

- Web global: **https://plataforma-total-web.pages.dev** (y espejo en GitHub Pages).
- Tu progreso web y desktop se sincronizan con tu alias+PIN.
- PWA: desde el celular, "Agregar a pantalla de inicio" → funciona offline con los 57 cursos.

---

## 🏠 Opción 4 — Levantar la WEB COMPLETA en tu PC (backend real local, U$S 0)

La misma app que corre en Cloudflare corre en tu máquina con el emulador oficial (wrangler dev),
**con base de datos SQLite local incluida** — ideal para probar antes de publicar:

```powershell
git clone https://github.com/SoftEngAi-dev/plataforma-total-pro.git
cd plataforma-total-pro\web
npm install
npx wrangler d1 execute plataforma --local --file=./schema.sql   # crea las 7 tablas locales
# (opcional) creá un archivo .dev.vars con:  ADMIN_SECRET=tu-secreto-de-pruebas
$env:ASTRO_BASE='/'; npm run build
npx wrangler pages dev --port 8788
```

→ Abrí **http://localhost:8788** : registro alias+PIN, sync de progreso, certificados
verificables, riel PRO manual (`POST /api/admin`)… todo funciona contra tu D1 local
(archivo en `web/.wrangler/state`). El Tutor IA usa tu cuenta de Cloudflare si hay AI binding;
el tutor propio de reglas funciona siempre offline.

---

## ❓ Solución rápida de problemas

| Síntoma | Solución |
|---|---|
| No abre / pantalla negra | Reejecutar el instalador como administrador; actualizar drivers gráficos |
| SmartScreen no deja instalar | "Más información" → "Ejecutar de todas formas" |
| Tutor IA no responde | Es normal sin Ollama: el tutor propio sigue funcionando; instalá Ollama para IA real |
| El progreso no aparece en la web | Las dos partes sincronizan al iniciar con tu alias+PIN conectado |

**Todo tu dato es tuyo**: SQLite local + archivos en tu PC. Nada se sube sin tu cuenta.
