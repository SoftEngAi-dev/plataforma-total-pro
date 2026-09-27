# Plataforma Total v5 — Local First

La aplicación tiene cuatro modos compatibles: Local, Local + IA, Hybrid y Cloud.

## Windows
Doble clic en `START-LOCAL.bat`. Para escritorio nativo, usar `run.bat`.

## Linux/macOS
```bash
chmod +x START-LOCAL.sh
./START-LOCAL.sh
```

La web local queda en `http://127.0.0.1:8787/`.

## Qué funciona sin Internet
Cursos, lecciones, quizzes, progreso local, certificados locales, proyectos locales, búsqueda y Tutor Propio por recuperación.

## IA local
Con Ollama activo en `127.0.0.1:11434`, el endpoint local de chat lo usa automáticamente. Sin Ollama, el servidor cae al tutor local por corpus.

## Datos
Windows: `%APPDATA%/PlataformaTotal`
Linux: `~/.local/share/PlataformaTotal`
macOS: `~/Library/Application Support/PlataformaTotal`

Se puede cambiar con `PT_DATA_DIR`.

## Web online
La infraestructura Cloudflare/D1/Workers AI existente se conserva. El contrato de progreso usa merge determinista: unión de lecciones/completados y máximos para contadores, evitando sobrescribir el progreso de otro dispositivo.


## Contrato de conexión v5.1

La fuente canónica del currículo es `contenido_a.py` … `contenido_f.py`. Antes de cada build se ejecuta `scripts/ensure_content.py`, que valida y, cuando hace falta, reconstruye los JSON de 57 cursos, 329 lecciones y 658 quizzes.

La capa web usa este orden:

`backend Cloudflare válido → API local/runtime → datos estáticos empaquetados → almacenamiento local`.

Un backend sólo se considera conectado si `/api/health` responde JSON con `ok=true` y `service=plataforma-total-api`.

Las funciones remotas principales son: `auth`, `progreso`, `pro`, `projects`, `certificado` y `chat`. Todas aceptan CORS para la web cross-origin.

En modo local, un token `local-...` nunca se envía a la nube. El progreso se mantiene en SQLite/IndexedDB y el Tutor puede funcionar con RAG local u Ollama.
