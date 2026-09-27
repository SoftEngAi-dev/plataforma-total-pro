# Plataforma Total v5.1 — Contrato de sistema y decisiones de integración

## 1. Fuente de verdad

El currículo vive en los módulos `contenido_a.py` … `contenido_f.py`.
`scripts/ensure_content.py` es el generador/validador de los artefactos web.

Contrato esperado:
- 57 cursos
- 17 FREE
- 40 PRO
- 329 lecciones
- 658 quizzes

Artefactos derivados:
- `web/public/data/indice.json`
- `web/public/data/cursos/*.json`
- `web/public/data/corpus.json`
- `web/public/offline-manifest.json`

## 2. Modos de ejecución

### Local
Runtime Python + SQLite. No requiere cuenta ni Cloudflare.

### Local + IA
Local con Ollama. Si Ollama no está disponible, Tutor Propio usa RAG sobre el corpus.

### Hybrid
La interfaz conserva datos locales y usa Cloudflare cuando el backend es válido.

### Cloud
Frontend + API en Cloudflare Pages, persistencia D1 y Workers AI.

## 3. Descubrimiento del backend

El frontend prueba `/api/health` y sólo considera válido un backend que responda JSON con:

`ok=true` + `service=plataforma-total-api`.

Una página HTML, un 404 o un timeout nunca se trata como API válida.

Backend canónico actual:
`https://plataforma-total-web.pages.dev/`

## 4. Datos y sincronización

El progreso se fusiona por entidad:
- unión de lecciones leídas
- unión de días activos
- unión de cursos completados
- máximo de XP
- máximo de contadores de quiz
- último `ultima` por timestamp

Los tokens `local-...` son locales y no se envían a Cloudflare.

## 5. Servicios

| Servicio | Local | Cloud |
|---|---|---|
| Cursos | JSON empaquetado | `/api/catalog` + `/api/course` |
| Progreso | SQLite/IndexedDB | D1 |
| Auth | sesión local | D1 + PBKDF2 |
| PRO | bandera local | D1 + Lemon Squeezy |
| Proyectos | almacenamiento local | D1 |
| Certificados | registro local | D1 |
| Tutor | RAG/Ollama | Workers AI + RAG |
| PWA | cache local | Pages |

## 6. Publicación

Cloudflare despliega la aplicación y API con `deploy-cloudflare.yml`.

GitHub Pages publica un espejo estático desde `docs/app`. El publicador:
1. genera currículo;
2. construye Astro con base `/plataforma-total-pro/app`;
3. copia la salida al destino correcto;
4. normaliza enlaces estáticos;
5. sincroniza `docs/app`;
6. hace rebase antes de `git push` para evitar carreras.

Los artefactos generados no vuelven a disparar el publicador.

## 7. Arranque

Windows:
`START-LOCAL.bat`

Linux/macOS:
`./START-LOCAL.sh`

Docker:
`docker compose up --build`

Desktop nativo:
GitHub Actions construye Windows, macOS y Linux.

## 8. Regla de funcionamiento

La aplicación nunca depende de que una capa visual “parezca conectada”.
Cada integración debe tener:
- endpoint real
- contrato JSON
- fallback definido
- prueba automatizada
- indicador de estado para el usuario
