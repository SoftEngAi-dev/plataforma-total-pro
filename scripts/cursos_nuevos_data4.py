#!/usr/bin/env python3
"""📚 Datos expansión — parte 4: Observabilidad (OpenTelemetry) y Tauri."""
Q = lambda p, ops, ok, exp: {"p": p, "ops": ops, "ok": ok, "exp": exp}
L = lambda t, x, q=None: {"t": t, "x": x.strip(), "q": q or []}

NUEVOS = [
{"slug": "56-observabilidad-otel", "free": False, "n": "🔭 Observabilidad — Logs, Métricas y Trazas con OpenTelemetry", "lecciones": [
L("1. Los 3 pilares: ver lo que pasa sin abrir la caja", """"Funciona en mi máquina" es una frase prohibida en producción. Observabilidad = poder responder "¿qué está pasando AHÍ ADENTRO?" sin redeployar.

Los 3 pilares (y su pregunta):
  📝 LOGS (eventos): "¿QUÉ pasó exactamente a las 03:12:44?" — texto estructurado por evento.
  📊 MÉTRICAS (series de números): "¿Cómo está la SALUD GENERAL?" — req/seg, latencia p95, CPU, errores/seg. Baratas de agregar y graficar.
  🔗 TRAZAS (recorrido de UNA petición): "¿DÓNDE se atascó ESTA request a través de 7 servicios?" — spans: gateway(2ms)→auth(45ms)→db(380ms)←🎯 ahí.

SLI/SLO — el lenguaje del acuerdo con el negocio:
  SLI (indicador): % de requests < 300 ms que respondieron OK
  SLO (objetivo): 99,9% mensual → presupuesto de error: 43 min/mes de fallo permitido
  → Si te queda presupuesto: podés deployar arriesgado. Si se acabó: estabilidad primero, features después. Así hablan ingeniería y negocio el mismo idioma.

El error fatal: "tenemos logs" ≠ observabilidad. 50 GB de logs de texto libre sin estructura son un pantano inutilizable. La observabilidad se DISEÑA (qué medir, con qué etiquetas) como se diseña la API: antes, no tras el incidente.""",
[Q("¿Qué pilar responde '¿en qué servicio se comió los 400 ms ESTA request concreta'?", ["Métricas", "Logs", "Trazas (spans anidados por servicio)", "El SLO"], 2, "La traza sigue UNA petición y descompone su tiempo por tramo: auth 45 ms + DB 380 ms = la respuesta al misterio."),
 Q("Tu SLO es 99,9% y ya consumiste el presupuesto de error del mes. ¿Qué toca?", ["Deployar más rápido", "Priorizar estabilidad sobre features hasta reponer presupuesto", "Bajar el SLO y listo", "Nada"], 1, "El error budget es una cuenta: cuando se gasta, el acuerdo serio es frenar riesgo. Así se negocia velocidad vs confianza con datos.")]),
L("2. Logs estructurados: que la máquina te ayude", """El log de texto libre ("algo falló xd") es para humanos del pasado. El LOG ESTRUCTURADO es JSON que se puede FILTRAR y AGREGAR:

  {"ts":"2026-09-21T03:12:44Z","nivel":"error","servicio":"api-auth",
   "evento":"login_fallido","alias":"dev_ana","motivo":"pin_incorrecto",
   "trace_id":"b4f2...","duracion_ms":87,"req_id":"r-8812"}

Ahora podés preguntar: "todos los error del servicio api-auth en la última hora con motivo=sesion_expirada" → una query, no grep artesanal en 6 máquinas.

Niveles con criterio (la inflación de logs es real y CARA: hay vendors que cobran por GB):
  DEBUG → solo en desarrollo (apagado en prod o sampling 1%)
  INFO  → hitos de negocio: user_registered, pago_completado
  WARN  → raro pero manejado: rate limit aplicado, retry que funcionó
  ERROR → acción requerida (humano despierta): cobro falló, DB inalcanzable

CORRELACIÓN (lo que los hace oro): un trace_id/request_id ÚNICO que atraviesa TODOS los logs de esa petición — 40 log-lines de 5 servicios quedan unidos como UNA historia.

Lo que JAMÁS se loguea (esto es examen de seguridad, no opinión):
  ✘ contraseñas/PIN/tokens/sesiones completas ✘ tarjetas ✘ PII sin enmascarar
  ✔ logueá HECHOS ("pin_incorrecto") sin SECRETOS.""",
[Q("¿Qué habilita el JSON estructurado que el log de texto no da?", ["Ocupa menos", "Filtrar/agregar por campos: 'errores de auth con motivo X en la última hora' sin grep artesanal", "Es más lindo", "Nada"], 1, "Los campos convierten el pantano en base de datos consultable: dashboards de logs, alertas por campo, agregaciones."),
 Q("¿Qué es lo ÚNICO que une 40 líneas de log de 5 servicios en una sola historia?", ["La hora", "El trace_id propagado por toda la cadena", "El nivel", "El formato"], 1, "Sin correlación tenés 40 eventos sueltos; con trace_id tenés la película completa de UNA petición.")]),
L("3. Métricas y alertas que no te despiertan por gusto", """Métricas = números con etiquetas en el tiempo:
  http_requests_total{metodo="POST", ruta="/api/chat", status="200"} 2451
  http_latencia_segundos_bucket{ruta="/api/chat", le="0.3"} 98%

Métodos de los 4 originales (Google) y RED — elegí según servicio:
  Latencia (p50/p95/p99), Tráfico (req/s), Errores (%), Saturación (qué tan lleno: CPU, cola).
Patrones dorados de alertamiento SERIO:
  ✔ Alerta sobre SÍNTOMA que afecta al usuario: "p95 de /api/chat > 3 s durante 10 min" 
  ✔ Con ventana: un pico de 1 min NO despierta a nadie; 10 min sostenidos sí.
  ✔ Multi-ventana (quema de presupuesto de error rápida vs lenta: 2% de error en 1 h = página; 0,5% en 3 días = ticket mañana).
  ✘ NO sobre causas internas genéricas ("CPU > 80%") — un pico de CPU sin impacto en el usuario es RUIDO que enseña a ignorar las alertas.

Regla de oro del 3 AM: TODA alerta que suene fuera de horario debe requerir acción humana INMEDIATA. Si no: es información para un dashboard, no para suenot.

Cardinalidad (la trampa de Prometheus): labels con valores infinitos (user_id como label) → millones de series → explota todo. Etiquetas: pocas, acotadas (ruta, método, status). El detalle por usuario va a LOGS, no a métricas.""",
[Q("¿Qué hace buena a una alerta 'p95 > 3 s durante 10 min'?", ["Despierta a alguien siempre", "Se basa en síntoma con impacto real y con ventana: descarta picos sin relevancia", "Mide CPU", "Es gratis"], 1, "Síntoma + duración: una alerta así solo suena cuando los usuarios realmente sufren de forma sostenida."),
 Q("¿Por qué nunca user_id como etiqueta de métrica?", ["Es feo", "Cardinalidad explota: cada usuario crea series nuevas y el sistema se cae", "Es ilegal", "Es lento de escribir"], 1, "Las etiquetas deben ser de bajo cardinalidad (ruta, status); los detalles de alta cardinalidad pertenecen a los logs.")]),
L("4. Trazas distribuidas y OpenTelemetry", """Cuando una request toca 8 servicios, los logs por servicio son 8 rompecabezas separados. La TRAZA los une: un árbol de SPANS (tramos con duración) con un trace_id común:

  POST /pagar                412ms
   ├─ auth.verificar          40ms
   ├─ inventario.reservar    180ms 🎯 ← 90% del tiempo acá
   │   └─ redis.eval         160ms
   ├─ pagos.cobrar           150ms
   └─ email.encolar           12ms

Un vistazo y sabés que el problema está en reservar/redis — sin adivinar, sin reuniones.

OpenTelemetry (OTel) es el ESTÁNDAR ABIERTO de instrumentación (el "OpenAPI" de la observabilidad): instrumentás UNA vez y exportás a cualquier backend (Jaeger/Tempo/Grafana/Honeycomb/Datadog) sin vendor lock-in.

  // JS: auto-instrumentación
  import { NodeSDK } from '@opentelemetry/sdk-node';
  const sdk = new NodeSDK({ /* OTLP exporter a tu colector */ });
  sdk.start();   // http, express, pg, fetch… quedan trazados solos

Propagación: el traceparent header atraviesa HTTP entre servicios — si UN eslabón no lo propaga, la traza se rompe ahí (lo verás como "agujeros").

Baggage: metadata que viaja con la traza (tenant, plan) — con eso graficás "latencia p95 por plan PRO vs FREE".

Sampling: trazar el 100% cuesta. Head-based sampling (1-10%) + tail-based (guardá SIEMPRE las trazas con error o lentas — ¡esas son las que importan!).""",
[Q("¿Qué resuelve OpenTelemetry como estándar?", ["Más métricas", "Instrumentás una vez y exportás a cualquier vendor sin lock-in", "Es otro agente privado", "Corre solo en Kubernetes"], 1, "Antes cada vendor pedía su propio agente: cambiar de Jaeger a Datadog = reinstrumentar. OTel es neutral: un esfuerzo, libertad de backend."),
 Q("Tu traza tiene un 'agujero' entre el gateway y el worker. Lo más probable es…", ["El worker no existe", "Ese eslabón no propaga el header traceparent: la traza se rompe ahí", "El trace está bien", "Falta RAM"], 1, "La propagación del contexto es manual entre procesos: si un salto no reenvía traceparent, lo posterior queda huérfano.")]),
L("5. Dashboards útiles e incidentes que se apagan", """Un dashboard NO es un collage de gráficos: es UNA historia por pestaña:
  • Página 1 "¿está todo bien?" (SLOs verdes/rojos, error budget al día)
  • Página 2 "salud por servicio" (RED por API: rate, errors, duration p95)
  • Página 3 "drill-down" (por ruta, por versión desplegada, por región)

Diseño que funciona: de lo global a lo específico (jerarquía), colores con significado (verde/ámbar/rojo = SLO, no decoración), y SIEMPRE una anotación del último deploy (el 70% de incidentes son cambios recientes: ver el deploy marcado en el gráfico responde la mitad de las preguntas sola).

Método de incidente (que no pánico):
  1. TRIAJE: ¿qué SLO está roto, cuántos usuarios, hay workaround? (nivel de severidad en 5 min)
  2. Hipótesis ORDENADA por probabilidad×velocidad de chequeo (¡último deploy primero!)
  3. Un canal, un comandante de incidente, log de decisiones en vivo
  4. MITIGAR PRIMERO (rollback es mitigación perfecta), diagnosticar después
  5. POSTMORTEM sin culpas: qué pasó, por qué no lo detectamos antes, 3-5 acciones con dueño y fecha. El mejor postmortem NO dice "fulano se equivocó": dice "el sistema permitió que fulano causara esto — ahora no permite".

Los incidentes se repiten en los equipos que culpan personas; desaparecen en los que arreglan sistemas.""",
[Q("El 70% de los incidentes correlaciona con…", ["La luna", "Cambios recientes (deploys): por eso el dashboard marca el último deploy", "El tráfico", "El calor"], 1, "La anotación del deploy en las gráficas responde la primera hipótesis gratis: '¿cambió algo?' casi siempre: sí, esto."),
 Q("En un incidente, mitigar ANTES de diagnosticar significa…", ["Ignorar la causa", "Rollback ya, análisis después: primero que el usuario vuelva a tener servicio", "Apagar todo", "Llamar al CEO"], 1, "Diagnosticar con presión cuesta 5× más. Mitigar (rollback/feature-flag off) devuelve el servicio y permite pensar con calma.")]),
L("6. Observabilidad gratis para proyectos chicos (como esta web)", """No todos pueden pagar Datadog (U$S 15-31/host/mes suma rápido). El stack de U$S 0 real:

  • LOGS: consola del worker + logs estructurados JSON (wrangler tail en tiempo real) → persiste en D1/R2 a futuro
  • MÉTRICAS: las que el proveedor ya mide gratis (Cloudflare Analytics: requests, status, latencia por ruta en el dashboard)
  • UPTIME: un ping cada 5 min desde fuera (un worker con cron o un monitor gratuito) → si la home no responde 200 te llega un alert/email
  • ERRORES: try/catch global que además del Response 500 guarde el error en una tabla 'errores' de D1 con contexto (ruta, stack, usuario) — tu Sentry casero de 30 líneas
  • TRAZAS: en monolitos/edge basta request_id + logs correlados (nuestro X-Token identifica sesión completa)

Los límites honestos del casero: retención corta, sin alertas sofisticadas multi-ventana, y cuando tu equipo crece el costo de MANTENERLO supera al de pagarlo. Señal de migración: cuando pasás más tiempo arreglando tu observabilidad que tu producto.

Roadmap profesional por etapas (copiable):
  Solo/MVP: logs JSON + uptime ping + tabla errores (esta web, hoy) ✅
  Primeros clientes: + Sentry free (errores frontend/backend), + métricas del proveedor
  Crecimiento: OTel + Jaeger/Tempo self-hosted o Grafana Cloud free tier (10k series, 50 GB logs)
  Equipo serio: vendor pago cuando el tiempo de tu equipo cueste más que la licencia""",
[Q("¿Cuál es la señal de que tu observabilidad casera debe migrar a solución paga/pro?", ["Un antivirus lo dice", "Cuando mantener tu observabilidad te quita más tiempo que el producto", "A los 100 usuarios", "Nunca"], 1, "La ecuación es tiempo de ingeniería vs licencia: al principio el casero gana; al crecer, mantenerlo se vuelve el impuesto oculto."),
 Q("El 'Sentry casero de 30 líneas' de este curso es…", ["Un antivirus", "try/catch global que guarda errores en una tabla D1 con ruta, stack y usuario", "Console.log", "Cloudflare Analytics"], 1, "Capturar excepciones con contexto en tu propia tabla ya te da el 80% del valor de un error tracker en un MVP.")])]},
{"slug": "57-tauri-apps-de-escritorio", "free": False, "n": "🦀 Tauri — Apps de Escritorio con Tu Stack Web", "lecciones": [
L("1. Tauri vs Electron: la dieta de 100 MB", """Electron (VS Code, Slack, Discord): cada app empaqueta Chromium + Node enteros → instalador 150-300 MB, RAM 300-800 MB por app idle.

Tauri: usa el WEBVIEW DEL SISTEMA OPERATIVO (WebView2 en Windows, WebKit en macOS/Linux — ya instalados) + backend en RUST → instalador de 3-15 MB, RAM ~50-100 MB idle.

  Electron:  [tu frontend] + [Chromium completo] + [Node] = 🐘
  Tauri:     [tu frontend] + [webview del SO] + [Rust chiquito] = 🐆

Bonus de seguridad por DISEÑO: el backend Rust expone SOLO los comandos que vos declarás (allowlist); el frontend no tiene Node al alcance (en Electron, nodeIntegration mal configurada = cualquier página externa ejecuta código de sistema — historial de CVEs largo).

Compatibilidad: si usás APIs súper específicas de Chromium, WebView2 (que ES Chromium Edge en Windows 10/11) te cubre; en Linux/macOS hay diferencias menores de WebKit — testeá en los 3.

Cuándo domina cuál:
  Startup velocidad-crítica, equipo JS puro → Electron (todo en un lenguaje)
  Apps chicas/seguras/distribución masiva, algo de Rust o ganas de aprender → Tauri
Esta plataforma usa Python+navegador propio (CustomTkinter) — el camino Tauri es el futuro natural si el front fuera puramente web + backend nativo chico.""",
[Q("¿De dónde sale la diferencia de 150+ MB entre Electron y Tauri?", ["Los íconos", "Electron empaqueta Chromium+Node enteros; Tauri usa el webview que el SO ya tiene", "Tauri comprime mejor", "Marketing"], 1, "El runtime pesado es la diferencia: compartir el webview del sistema en vez de traer uno propio cambia toda la ecuación."),
 Q("La seguridad por defecto de Tauri frente a Electron radica en…", ["Es más caro", "Allowlist de comandos Rust; el frontend no tiene Node alcanzable por defecto", "Usa HTTPS", "El antivirus"], 1, "Expone solo lo declarado: ninguna página externa inyectada en tu webview puede tocar el sistema sin permiso explícito.")]),
L("2. Tu primera app Tauri en 15 minutos", """Requisitos: Rust + Node (y WebView2 en Windows).

  npm create tauri-app@latest   # elige plantilla: vanilla, React, Vue, Solid…

Estructura:
  mi-app/
    src/            ← tu frontend web NORMAL (HTML/JS/CSS, cualquier stack)
    src-tauri/      ← el backend Rust
      src/main.rs
      tauri.conf.json   ← nombre, versión, íconos, ventana, permisos
      Cargo.toml

  npm run tauri dev     → app nativa en tu pantalla con hot-reload del front
  npm run tauri build   → .msi / .dmg / .AppImage optimizados (¡7 MB!)

El frontend no cambia: tu fetch()/CSS/frameworks corren igual — son un sitio web en una ventana sin chrome de navegador.

tauri.conf.json decisiones clave:
  • "identifier": "com.tuapp.dev" (único, formato reverse-domain)
  • ventana: tamaño, resizable, fullscreen
  • seguridad: "csp" y la allowlist de capabilities por comando

El ciclo de aprendizaje: dev = instantáneo (webview recarga), build = minutos la primera vez (compila Rust), despues incremental.""",
[Q("¿Qué hay que reescribir de tu frontend web para meterlo en Tauri?", ["Todo", "Nada: corre igual en el webview nativo (tu stack web sin cambios)", "El CSS", "Las rutas"], 1, "Tu HTML/JS/CSS/framework va tal cual: la ventana de Tauri es un navegador sin pestañas — la migración es de empaquetado, no de código."),
 Q("tauri.conf.json define…", ["Solo el ícono", "Identificador único, ventana, permisos/capabilities y empaquetado", "La DB", "El CSS"], 1, "Es el manifiesto de la app: nombre, seguridad (CSP, allowlist), ventana y cómo se generan .msi/.dmg/.AppImage.")]),
L("3. Commands: el puente JS ↔ Rust", """El webview no tiene fs ni procesos: el poder nativo lo da Rust mediante COMMANDS declarados:

  // src-tauri/src/main.rs
  #[tauri::command]
  fn saludar(nombre: String) -> String {
      format!("Hola, {nombre}! Desde Rust 🦀")
  }

  #[tauri::command]
  async fn leer_config() -> Result<String, String> {
      tokio::fs::read_to_string("config.json").await
          .map_err(|e| e.to_string())   // Result → error manejable en JS
  }

  fn main() {
      tauri::Builder::default()
          .invoke_handler(tauri::generate_handler![saludar, leer_config])
          .build(tauri::generate_context!())
          .expect("error al arrancar");
  }

  // y en tu JS:
  import { invoke } from '@tauri-apps/api/core';
  const saludo = await invoke('saludar', { nombre: 'Ana' });
  const cfg = await invoke('leer_config').catch(e => console.error('falló:', e));

El modelo mental es IPC explícito: cada capacidad que el frontend necesita (leer archivos, DB, red baja nivel, tray) se registra como comando = AUDITABLE. ¿Qué puede hacer esta app? Leés la lista de commands y lo sabés — esa es la seguridad práctica.

Eventos bidireccionales: Rust puede EMITIR eventos (progreso de descarga, "archivo cambió") que el frontend escucha con listen() — el canal del backend hacia la UI en tiempo real.""",
[Q("¿Cómo accede el frontend de Tauri al sistema de archivos?", ["Directo como en Node", "Solo mediante #[tauri::command] de Rust declarado y auditables", "Con require('fs')", "por JSONP"], 1, "El webview queda aislado: toda capacidad nativa es un comando Rust explícito — superficie de ataque mínima y listada."),
 Q("Para progreso en tiempo real del backend hacia la UI se usa…", ["Polling cada 10 ms", "Eventos: Rust emite, el frontend escucha con listen()", "localStorage", "Cookies"], 1, "El canal de eventos evita polling: descargas, watchers de archivos y logs llegan push-style al front.")]),
L("4. Plugins oficiales: superpoderes sin escribir Rust", """El ecosistema de plugins oficiales cubre el 90% de las necesidades nativas: se agregan en un comando y quedan disponibles en JS:

  cargo add tauri-plugin-fs          # leer/escribir archivos CON permisos granulares
  cargo add tauri-plugin-dialog      # open/save nativos del SO
  cargo add tauri-plugin-notification
  cargo add tauri-plugin-sql         # SQLite con migraciones (¡tu DB local!)
  cargo add tauri-plugin-store       # key-value persistido (config/settings)
  cargo add tauri-plugin-http        # fetch desde Rust (sin CORS del webview!)
  cargo add tauri-plugin-shell       # ejecutar comandos permitidos
  cargo add tauri-plugin-updater     # auto-actualización con firma (lección 5)
  cargo add tauri-plugin-global-shortcut   # hotkeys globales estilo Spotlight

  import { readTextFile } from '@tauri-apps/plugin-fs';
  const txt = await readTextFile('notas.txt', { baseDir: BaseDirectory.AppData });

CAPABILITIES (permiso = archivo, no comentario): cada plugin exige declarar en capabilities/ QUÉ puede hacer — p.ej. fs solo dentro de $APPDATA, shell solo el binario 'pandoc'. Si atacan tu webview, solo consiguen lo que vos declaraste (o menos).

El patrón de diseño recomendado: lo visual/complejo → JS+plugin oficial; lo crítico/sensible/rendimiento → comando Rust propio. Blend sano.""",
[Q("¿Qué garantiza el sistema de capabilities de plugins?", ["Rapidez", "Cada capacidad nativa está declarada y acotada por archivo (fs solo en AppData, shell solo binarios listados)", "Nada", "Todo abierto"], 1, "Permiso declarativo y granular: una webview comprometida hereda solamente lo declarado — el resto del sistema es invisible."),
 Q("¿Por qué tauri-plugin-http evita los errores de CORS?", ["Es HTTP/3", "Las peticiones salen desde Rust (fuera del webview): sin reglas de origen del navegador", "Usa VPN", "No hace falta"], 1, "Scraping/APIs propias sin fricción: el fetch corre en el proceso Rust, no en el navegador — CORS no aplica ahí.")]),
L("5. Empaquetar, firmar y auto-actualizar", """Distribuir escritorio serio = 3 problemas reales: formato, firma y updates.

BUNDLES por SO:
  Windows: .msi (y .exe NSIS)      macOS: .app/.dmg (firmado con certificado Apple Developer U$S 99/año)
  Linux: .AppImage/.deb/.rpm
  tauri build los genera todos (mejor en CI: matriz de runners, como hace esta plataforma con GitHub Actions para su .exe).

FIRMA (la diferencia usuarios-confían vs "Windows protegió su PC" azul):
  Windows: certificado de código (comercial ~U$S 100-300/año; sin él, SmartScreen asusta)
  macOS: sin notarización de Apple, Gatekeeper BLOQUEA la app directamente.
  Linux: no firma obligatoria.

AUTO-UPDATE con tauri-plugin-updater:
  1. Publicás un JSON con la última versión + URLs firmadas (en GitHub Releases va perfecto)
  2. La app al arrancar consulta: "¿hay > 1.4.0?"
  3. Descarga, VERIFICA FIRMA ED25519, instala, reinicia — el usuario no hace nada (como nuestra app desktop, que hace lo propio con releases de GitHub)

  { "version": "1.4.1", "pub_date": "2026-09-21",
    "platforms": { "windows-x86_64": { "url": "...msi", "signature": "..." } } }

Errores a evitar: actualizar porque sí (interrumpís trabajo: mejor "nueva versión disponible" no intrusivo), no verificar firma (¡vector de ataque!), y no tener rollback (si la nueva crashea, que el update anterior siga usable hasta el próximo arranque).""",
[Q("¿Por qué la firma de código importa tanto en distribución?", ["Es legal bonito", "Sin firmar, Windows SmartScreen/Gatekeeper bloquean o asustan al usuario en la instalación", "Para SEO", "Para el antivirus"], 1, "Windows asusta con pantalla azul y macOS bloquea de plano sin notarización: la firma es el pasaporte de tu app."),
 Q("La pieza crítica de seguridad del auto-updater es…", ["Descargar rápido", "Verificar la FIRMA del paquete antes de instalarlo", "El JSON bonito", "Reiniciar siempre"], 1, "Un updater sin verificación de firma es un instalador remoto de malware: la firma Ed25519 valida que el paquete es tuyo.")]),
L("6. Casos de éxito y límites honestos", """WINS reales 2024-2026: el ecosistema migró masivamente — herramientas de dev de referencia lo adoptaron por tamaño+memoria (el gap frente a Electron en idle es ×5-10): editores y notas, dashboards de DB, launchers de juegos, agents de IA locales, y apps internas empresariales. La comunidad Rust lo empuja fuerte y la versión 2.x lo estabilizó.

Fortalezas que deciden:
  ✔ Binario ridículamente chico → distribución fácil (¡adjuntálinseter en un email!)
  ✔ Seguridad by-design (allowlist, CSP, sin Node expuesto)
  ✔ Un solo codebase front: tu web app existente se vuelve desktop en días
  ✔ 2026: soporte MÓBILE (iOS/Android) en maduración — el sueño del codebase total

LÍMITES honestos:
  ✘ Algo de Rust es inevitable a medida que crece (¡bendición disfrazada para aprender!)
  ✘ WebView2 no siempre está en Windows viejo/corporativos (hay que bootstraparlo)
  ✘ Diferencias sutiles WebKit/Lin vs Chromium/Win: CSS/features raras → test en los 3 SO
  ✘ APIs muy Chromium-específicas no existen
  ✘ Móvil aún joven (madura, pero no al nivel del desktop)

La decisión práctica final:
  • equipo JS puro, deadline brutal, sin interés en nativo → Electron o PWA
  • producto a largo plazo, seguridad/eficiencia valoradas → TAURI
  • app offline intensiva en Python ya hecha (¡como esta!) → lo que ya funciona, hasta que el front web pida puente nativo""",
[Q("El límite práctico más frecuente al adoptar Tauri es…", ["Usa mucha RAM", "Eventualmente algo de Rust hay que escribir (y WebView2 se debe bootstrappe en Windows viejos)", "No corre en Windows", "Es pago"], 1, "El 90% se cubre con plugins, pero el 10% nativo pide Rust — que es justamente el incentivo para aprenderlo con propósito."),
 Q("Tu app web ya existe y querés desktop en días. El camino Tauri es…", ["Reescribir en Rust todo", "Meter el webview de tu web tal cual + agregar comandos/plugins solo donde el navegador no llega", "No se puede", "Flutter mejor"], 1, "El front migra gratis (es tu web); el trabajo incremental vive solo en las capacidades nativas que agregás bajo demanda.")])]},
]

print("✔ cursos_nuevos_data4 cargado:", len(NUEVOS), "cursos")
