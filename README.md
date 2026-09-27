<p align="center">
  <img src="assets/icono-256.png" width="140" alt="Plataforma Total 🎓">
</p>

# 🎓 Plataforma Total — Escuela de Programación + IA

[![CI](https://github.com/SoftEngAi-dev/plataforma-total-pro/actions/workflows/ci.yml/badge.svg)](https://github.com/SoftEngAi-dev/plataforma-total-pro/actions)
[![Desktop Build](https://github.com/SoftEngAi-dev/plataforma-total-pro/actions/workflows/build.yml/badge.svg)](https://github.com/SoftEngAi-dev/plataforma-total-pro/actions)
[![Licencia MIT](https://img.shields.io/badge/licencia-MIT-22c55e)](LICENSE)
[![Web](https://img.shields.io/badge/web-PWA-f59e0b)](https://softengai-dev.github.io/plataforma-total-pro/)

**v5.1.0 · 57 cursos · 329 lecciones · 658 quizzes · 17 cursos FREE + 40 PRO.**

Plataforma Local First para aprender programación, practicar, medir progreso y utilizar IA local opcional. Funciona como aplicación desktop y como web/PWA.

## 🚀 Empezar ahora

### Opción 1 — Windows: runtime local completo
Instala Python 3.10+ y Node.js LTS, clona el repositorio y ejecuta:

```bat
git clone https://github.com/SoftEngAi-dev/plataforma-total-pro.git
cd plataforma-total-pro
START-LOCAL.bat
```

Se abre en `http://127.0.0.1:8787/`. La primera ejecución crea el entorno virtual, instala dependencias y construye la web.

### Opción 2 — Linux/macOS: runtime local completo

```bash
git clone https://github.com/SoftEngAi-dev/plataforma-total-pro.git
cd plataforma-total-pro
chmod +x START-LOCAL.sh
./START-LOCAL.sh
```

### Opción 3 — Aplicación desktop nativa
GitHub Actions compila automáticamente Windows, macOS y Linux.

1. Abre **Actions** → **🖥️ Compilar ejecutables desktop**.
2. Selecciona una ejecución exitosa.
3. Descarga `PlataformaTotal-Windows`, `PlataformaTotal-macOS` o `PlataformaTotal-Linux`.
4. En Windows, descomprime el ZIP y ejecuta `PlataformaTotal.exe`.

Los artefactos de Actions son temporales. Para crear una descarga permanente, publica un tag `v5.0.0`; el workflow de release adjunta los tres paquetes automáticamente.

## 🌐 Versión online

La versión pública se despliega mediante GitHub Pages:

**https://softengai-dev.github.io/plataforma-total-pro/**

La infraestructura Cloudflare/D1/Workers AI del repositorio queda disponible para el modo cloud/híbrido cuando se configuren sus credenciales y bindings.

## 🏠 Local First

La v5 incorpora:

- SQLite local para el runtime de escritorio/web local.
- IndexedDB para persistencia del navegador.
- PWA/offline y precarga del contenido FREE.
- Sincronización con merge determinista.
- Proyectos locales.
- Certificados locales.
- Tutor IA con RAG local y Ollama opcional.
- API local sin necesidad de Cloudflare para estudiar.

Guía completa: [LOCAL-FIRST.md](LOCAL-FIRST.md).

## 🧠 IA local con Ollama

Con Ollama ejecutándose en `127.0.0.1:11434`, el Tutor local puede utilizar el modelo instalado. Sin Ollama, funciona el tutor de recuperación sobre el corpus local.

Ejemplo:

```bash
ollama pull llama3.2:3b
```

También existe `docker-compose.yml` para levantar el runtime local junto con Ollama.

## 📚 Contenido

**57 cursos · 329 lecciones · 658 quizzes**

Incluye web, JavaScript, TypeScript, React, Node.js, Python, SQL/PostgreSQL, PHP/Laravel, Ruby/Rails, Java/Spring, C#/.NET, Go, Rust, C/C++, móvil, frameworks, datos, IA/LLMs, testing, seguridad, arquitectura, APIs, DevOps y carrera profesional.

## 🗂️ Estructura principal

| Ruta | Función |
|---|---|
| `main.py` | Aplicación desktop |
| `contenido_*.py` | Fuente curricular |
| `web/` | Astro + PWA + APIs |
| `local_server.py` | Runtime local con SQLite |
| `platform.json` | Contrato de capacidades y estadísticas |
| `web/public/data/` | Corpus web |
| `tests/test_integridad.py` | Integridad del contenido |
| `.github/workflows/ci.yml` | CI, E2E y smoke test local |
| `.github/workflows/build.yml` | Compilación Windows/macOS/Linux |
| `START-LOCAL.bat` | Arranque Windows |
| `START-LOCAL.sh` | Arranque Linux/macOS |
| `docker-compose.yml` | Runtime local + Ollama |

## 🔐 Datos y privacidad

El modo local almacena los datos fuera del repositorio:

- Windows: `%APPDATA%/PlataformaTotal`
- Linux: `~/.local/share/PlataformaTotal`
- macOS: `~/Library/Application Support/PlataformaTotal`

Puedes cambiarlo con `PT_DATA_DIR`.

## 🧪 Estado verificado de v5.0.0

La capa web es Local First: valida el backend antes de usarlo y mantiene un fallback local real para datos, sesión, progreso, chat, proyectos y certificados. El currículo se regenera desde `contenido_a.py` … `contenido_f.py`.

El commit actual de `main` pasa:

- integridad de contenido: **OK**
- build Astro: **OK**
- E2E contra Wrangler local: **OK**
- runtime local: **OK**
- ejecutable Windows: **OK**
- ejecutable macOS: **OK**
- ejecutable Linux: **OK**
- GitHub Pages deployment: **OK**

## 📖 Documentación

- [LOCAL-FIRST.md](LOCAL-FIRST.md)
- [MONETIZACION.md](MONETIZACION.md)
- [CHANGELOG.md](CHANGELOG.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)

## 📜 Licencia

MIT.
