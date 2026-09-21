#!/usr/bin/env python3
"""📚 Datos expansión — parte 3: Cloudflare/Edge, Qwik/Solid/Señales, Data moderna."""
Q = lambda p, ops, ok, exp: {"p": p, "ops": ops, "ok": ok, "exp": exp}
L = lambda t, x, q=None: {"t": t, "x": x.strip(), "q": q or []}

NUEVOS = [
{"slug": "53-cloudflare-y-edge-computing", "free": False, "n": "☁️ Cloudflare y Edge Computing — Serverless Real (Caso: Esta Web)", "lecciones": [
L("1. Edge: tu código vive en 300 ciudades", """El cloud clásico: tu servidor corre en 1 región (Virginia). Un usuario de Tokio: 250 ms de ida y vuelta POR REQUEST.

Edge computing: tu función corre en ~300 ciudades del mundo, en el POP (punto de presencia) más cercano a cada usuario. Tokio → 5 ms.

Cloudflare Workers = la referencia del modelo:
  • V8 isolates (NO containers): arranque 0 ms (cold start inexistente — Lambda/AWS tarda 300 ms-segundos)
  • Escala sola de 0 a millones de requests y vuelve a 0: no hay "servidor" que pagar encendido
  • Free tier: 100.000 requests/día

No es magia: tu código se copia a todos los POPs. Lo difícil no es el código: son LOS DATOS (la base sigue centralizada — lección 3).

Candidatos ideales para edge:
  ✔ auth/validación de tokens (¡nuestro /api/auth con PBKDF2 corre en el edge!)
  ✔ APIs ligeras, webhooks, redirects, A/B tests, middleware
  ✔ SSR cerca del usuario
  ✘ trabajos largos (free: 10 ms CPU/request), ✘ estado en memoria entre requests

Esta plataforma ES el caso de estudio: 8 Functions en producción, U$S 0, sirviendo a estudiantes desde Uruguay con latencia mínima.""",
[Q("¿Qué permite a Cloudflare Workers arrancar en 0 ms cuando Lambda tarda cientos?", ["Más RAM", "V8 isolates en vez de containers: no hay SO que bootear", "Magia", "Menos seguridad"], 1, "El isolate de V8 comparte proceso con otros: tu contexto se crea en milisegundos. El container necesita bootear un OS completo."),
 Q("¿Cuál es la dificultad REAL de arquitectura edge (que no es el código)?", ["Los datos: tu función viaja, pero la base de datos sigue centralizada", "El DNS", "La RAM", "El firewall"], 0, "El cómputo se multiplica a 300 POPs gratis; la consistencia y cercanía de los DATOS es el problema de diseño que queda.")]),
L("2. Workers en serio: bindings, límites y nuestro caso", """Un Worker es un fetch handler:

  export default {
    async fetch(request, env, ctx) {
      const url = new URL(request.url);
      if (url.pathname === '/api/hola')
        return Response.json({ ok: true, ciudad: request.cf.city });
      return new Response('nada acá', { status: 404 });
    }
  }

BINDINGS: cómo el worker toca el mundo — se configuran en wrangler.toml y llegan como env:
  [[d1_databases]]   → env.DB (SQLite en el edge)
  [ai]               → env.AI (Workers AI — nuestra IA)
  [[kv_namespaces]]  → env.KV (key-value global)
  [[r2_buckets]]     → env.R2 (almacenamiento de objetos)

LÍMITES free tier (2026): 10 ms de CPU por request (ojo: SIEM, PBKDF2 con 100k iteraciones entra justo — el wall-time ilimitado pero el CPU se mide), 128 MB RAM, sin sockets arbitrarios (hay fetch, WebSocket y connect() TCP en paid).

Errores típicos de novato:
  • Usar APIs de Node (fs, process.env) — el runtime NO es Node: es V8 puro con WinterCG (hay compat layer nodejs_compat para lo básico)
  • Guardar estado en variables globales entre requests (el isolate puede reciclarse: NUNCA asumas memoria)
  • Secretos hardcodeados → wrangler secret put LS_SECRET (nuestro caso: el secreto del webhook de Lemon Squeezy vive así, cifrado)

wrangler pages deploy: así está en producción esta web: Pages (estáticos) + Functions (workers) vendos juntos = hybrid SSR.""",
[Q("¿Cómo recibe un Worker el acceso a la base D1?", ["Conexión TCP a Postgres", "Como binding en el objeto env (configurado en wrangler.toml)", "Por HTTP con password", "No puede"], 1, "Los bindings (env.DB, env.AI, env.KV) son la forma declarativa de vincular recursos — cero strings de conexión en el código."),
 Q("¿Por qué NO debés guardar datos entre requests en variables globales del Worker?", ["Ocupa mucho", "El isolate puede reciclarse o replicarse en otro POP: no hay garantías de memoria persistente", "Rompe CORS", "Es ilegal"], 1, "Cada request puede aterrizar en otro isolate u otra ciudad. El estado va en D1/KV/R2, nunca en memoria.")]),
L("3. Datos en el edge: D1, KV y R2 (cuándo cada uno)", """El trilema del edge: global, consistente, rápido — elegí dos por servicio y combiná.

🗄️ D1 (SQLite serverless): SQL relacional de verdad.
  Uso: datos relacionales que cambian seguido (users, sessions, progreso — literal: las 7 tablas de esta plataforma).
  Modelo: 1 primario + réplicas de lectura; las ESCRITURAS van al primario (si tu usuario está lejos, la escritura tiene latencia — es el precio de la consistencia).
  Free: 5M lecturas/día, 100k escrituras/día, 500 MB.

⚡ KV (key-value global): el más rápido de lectura (~60 s de propagación de escrituras).
  Uso: config, feature flags, sesiones cacheables, tokens de un solo uso. Consistencia EVENTUAL: escribís en Tokio y en Uruguay puede tardar ~1 min en verse.

📦 R2 (object storage, S3-compatible sin egress fees!): archivos, imágenes, backups, el esquema SQL.
  El killer feature: $0 de egreso (AWS te cobra fortuna por sacar TUS datos).

Patrón real (esta web): auth y progreso viven en D1 (consistencia > cercanía), los assets estáticos globales los sirve el CDN de Pages (cache infinito), los certificados se generan cliente-side y solo se REGISTRA el código en D1.

¿Y cuando necesitás estado coordinado en vivo (chat, multiplayer)? → Durable Objects (lección final).""",
[Q("Tu app guarda quién es PRO tras un pago. ¿KV o D1?", ["KV: es más rápido", "D1: la compra es relacional y la consistencia importa; KV es eventual", "R2", "localStorage"], 1, "KV puede tardar ~1 min en propagar: mostrarías 'no sos PRO' habiendo pagado. Compras y relaciones → D1; cache y flags → KV."),
 Q("El mayor argumento económico de R2 frente a S3 es…", ["Es más grande", "$0 de egreso fees: sacar tus datos no cuesta", "Tiene SQL", "Es de Google"], 1, "AWS cobra carísimo sacar datos (egress). R2 lo deja en cero — el motivo #1 de migraciones 2024-2026.")]),
L("4. Pages Functions y CORS: nuestro deploy real, desarmado", """El híbrido que esta misma plataforma usa en plataforma-total-web.pages.dev:

  Pages  → sirve /dist (las 14 páginas estáticas) en el CDN global
  Functions → /api/* corre como Workers (SSR hybrid del adaptador Astro)

CORS — por qué el navegador bloquea y cómo se abre BIEN:
  El frontend vive en github.io (estático, espejo) y el backend en pages.dev → petición CROSS-ORIGIN. El navegador manda primero un preflight OPTIONS:

  Access-Control-Request-Method: POST
  ← NUESTRO worker responde:
  HTTP 204
  access-control-allow-origin: *
  access-control-allow-headers: Content-Type, X-Token
  access-control-allow-methods: GET, POST, OPTIONS

  En cada endpoint exportamos también OPTIONS:
  export const OPTIONS = () => new Response(null, { status: 204, headers: CORS });

Errores clásicos:
  • Responder OPTIONS pero olvidar el header en las respuestas NORMALES (el preflight pasa y la petición real falla 🤡)
  • Origin: * CON credentials: 'include' (prohibido por spec: con cookies debe ser origin exacto)
  • Preflight cache: Access-Control-Max-Age te ahorra preflights repetidos.

El CORS NO es seguridad de servidor (se bypasse con curl): es seguridad para proteger al USUARIO de sitios maliciosos. La seguridad real: tokens y firma HMAC (como en nuestro webhook de pagos).""",
[Q("¿Qué es el preflight OPTIONS y cuándo se dispara?", ["Siempre", "Antes de una petición cross-origin con headers/métodos no-simples: el navegador pide permiso primero", "Solo en localhost", "Solo con GET"], 1, "Content-Type: application/json o X-Token en cross-origin ya disparan preflight. Respondés 204 + allow-* y recién ahí va la petición real."),
 Q("¿Por qué 'Access-Control-Allow-Origin: *' + cookies está PROHIBIDO por la spec?", ["Porque sí", "Cualquier sitio podría robar respuestas autenticadas del usuario; con credentials el origin debe ser exacto", "Rompe el cache", "No está prohibido"], 1, "* + credentials sería el fin del mundo web: cualquier página leería tus sesiones. Por eso con cookies usás origin explícito.")]),
L("5. Workers AI: GPUs del planeta a 1 línea", """Workers AI pone el catálogo de modelos open (Llama, Mistral, Whisper, embeddings, visión) en los GPUs de Cloudflare, facturando en "neurons" (unidad de cómputo con Ia). En el free tier: 10.000 neurons/día.

  env.AI.run('@cf/meta/llama-3.3-70b-instruct-fp8-fast', {
    messages: [{ role: 'user', content: 'Explicá closures' }]
  })

Lecciones duras de nuestra producción (esta web):
  1. LOS MODELOS SE DEPRECAN: llama-3.1-8b desapareció del catálogo en mayo 2026 y nuestro endpoint empezó a tirar error. Solución: cadena de fallbacks (3.3-70b → 3.2-3b) y consultar el catálogo por API antes de hardcodear.
  2. Max_tokens cortá respuestas: puede cortar a la mitad — detectá y re-preguntá "continuá".
  3. El streaming (SSE) vale la pena para UX: la primera palabra en ~300 ms vs 4 s de espera muda.
  4. Neurons no son tokens: un modelo grande cobra más por token — medí tu cuota contra tu tráfico (10k neurons ≈ 100 chats medianos/día con 70b).

Casos que funcionan free: chat moderado, resúmenes, clasificación, embeddings (bge — nuestro plan para el tutor híbrido). Para escala: AI Gateway (analytics, caché, rate-limiting y fallback entre PROVEEDORES distintos: CF→OpenAI→Anthropic con una sola línea).""",
[Q("Nuestro /api/chat dejó de funcionar en 2026. ¿Lección de arquitectura?", ["No usar IA", "Los modelos hosted se deprecan: siempre cadena de fallbacks y catálogo consultable", "Pagar más", "Es bug nuestro"], 1, "La dependencia de terceros cambia bajo tus pies: fallback automático (70b→3b) y el código preparado para sumar modelos nuevos."),
 Q("¿Para qué sirve AI Gateway?", ["Comprar GPU", "Analytics, caché de respuestas, rate-limit y fallback entre proveedores de IA distintos en un solo punto", "Más neurons", "Base de datos"], 1, "Es el proxy de tu IA: si un proveedor se cae o se encarece, cambiás al siguiente sin tocar la app — y de yapa cachea.")]),
L("6. Durable Objects: estado coordinado en el caos distribuido", """Workers: stateless. KV: eventual. D1: SQL. ¿Y si necesito UN punto que coordine estado en vivo (chat room, juego multiplayer, contador global exacto)? → DURABLE OBJECTS.

Un DO es una clase JS con almacenamiento transaccional propio que vive en UN lugar del mundo (el primero que lo invoca) y tiene ID único:

  export class SalaDeChat {
    constructor(state, env) { this.state = state; this.sockets = new Set(); }
    async fetch(request) {
      // acepta WebSocket, difunde mensajes a this.sockets, guarda historial en this.state.storage
    }
  }
  // cada sala: env.SALAS.idFromName("sala-42") → misma instancia SIEMPRE

La magia: idFromName() garantiza que TODOS los mensajes de "sala-42" llegan a LA MISMA instancia (routeo global incluido). Estado consistente sin pensar en réplicas.

WebSocket Hibernation (lo moderno): la sala "duerme" sin conexiones activas cobrando CPU — miles de salas idle cuestan centavos.

Casos ideales: chat, documentos colaborativos (¡base de CRDTs!), presencia online, rate limiting distribuido exacto, locks globales, turnos en juegos.

Level-up mental: Workers + D1 + KV + R2 + DO + AI cubren el 100% de un producto SaaS moderno con CERO servidores propios. El free tier te deja validar el negocio; los precios por uso crecen SOLO cuando tus ingresos también. Esta plataforma es la prueba viva: *8 endpoints, 7 tablas, IA, webhook HMAC, U$S 0*.""",
[Q("¿Qué problema resuelve un Durable Object que Workers + KV no resuelven?", ["Guardar archivos", "Coordinación de estado EN VIVO en un punto único consistente (chat, multiplayer, locks)", "Más RAM", "SQL"], 1, "DO te da una instancia ÚNICA por ID con storage transaccional: la pieza para colaboración en tiempo real que el resto del modelo no cubre."),
 Q("WebSocket Hibernation permite…", ["Más velocidad", "Salas con conexiones idle dormidas sin cobrar cómputo: miles de chats inactivos casi gratis", "Cerrar sockets", "IPv6"], 1, "La conexión WS persiste pero la instancia 'duerme' cuando no trafica — el modelo de precios que hace viables chats masivos.")])]},
{"slug": "54-qwik-solid-y-senales", "free": False, "n": "🌊 Qwik, Solid y Señales — El Frontend que Viene", "lecciones": [
L("1. El problema: la hidratación mata", """2020s: SSR + hidratación. El servidor manda HTML ✔… y después el navegador DESCARGA TODO EL JS y "re-vive" cada componente para hacerlo interactivo (hydration). En un e-commerce: 400 KB de JS para que 3 botones funcionen. Lighthouse llora.

Los datos duros: cada 100 ms de retraso en móvil ≈ −1% conversión. Y el hydration es trabajo DUPLICADO: el servidor ya renderizó; el cliente re-ejecuta TODO tu código para reconstruir el estado.

Las tres salidas de la industria:
  1️⃣ ISLAS (Astro): solo los componentes interactivos hidratan; el resto es HTML muerto. (¡Esta web!)
  2️⃣ SEÑALES (Solid, Preact Signals, Angular Signals): reactividad fina sin re-render ni Virtual DOM.
  3️⃣ RESUMABILIDAD (Qwik): cero hydration: el estado SERIALIZA en el HTML y el cliente "reanuda" donde quedó el servidor.

Consecuencia real: páginas que eran 3,2 s de TTI (time-to-interactive) pasan a 0,9 s en el mismo contenido. En Core Web Vitals se nota en el ranking y en la factura de ads.

No es hype ciego: son ideas viejas (reactividad de Knockout 2010, serialización de estado de los videojuegos) con ingeniería de 2024.""",
[Q("¿Qué es exactamente la 'hidratación'?", ["CSS", "Descargar y ejecutar TODO el JS para revivir cada componente del HTML ya renderizado", "SEO", "Un cache"], 1, "Es trabajo duplicado: el servidor ya hizo el render; el navegador re-ejecuta para atar eventos. El precio: TTIs enormes."),
 Q("¿Qué comparten islas, señales y resumabilidad?", ["Usan jQuery", "Diferentes caminos para eliminar trabajo innecesario de arranque en el navegador", "Son SSR", "Usan WASM"], 1, "Las tres estrategias atacan el mismo problema: hacer interactivo solo lo necesario, lo más barato posible.")]),
L("2. Señales: reactividad quirúrgica (Solid)", """React re-renderiza el COMPONENTE entero ante cada cambio y luego hace "diffing" con el Virtual DOM para ver qué cambió de verdad. Solución 2013 honesta, pero con costo: recorres un árbol para cambiar un <span>.

Las SEÑALES (Solid/Signals): valores que SABEN quién los usa y actualizan EXACTAMENTE ese punto del DOM:

  import { createSignal } from "solid-js";
  const [cuenta, setCuenta] = createSignal(0);
  <button onClick={() => setCuenta(cuenta() + 1)}>
    Clicks: {cuenta()}
  </button>

Al compilar, Solid detecta que SOLO ese {cuenta()} depende de la señal y genera código que actualiza ESE textNode. No hay re-render del componente. No hay VDOM que comparar. No hay re-renders misteriosos de memo/useMemo/useCallback (adiós a esa trinidad de dolores).

Consecuencias:
  • Rendimiento: Solid está ~al nivel de vanilla JS en benchmarks (y por encima de React/Vue en mutaciones).
  • Modelo mental simple: el componente corre UNA VEZ (setup); luego solo los efectos reactivos.
  • Computados y efectos: createMemo (valor derivado cacheado), createEffect (efecto ante cambio).

Costo: ecosistema más chico (librerías de UI, ejemplos, empleo). Es el trade: menos masa crítica, mejor física.""",
[Q("¿Qué evita Solid que React hace en cada cambio de estado?", ["El navegador", "Re-renderizar el componente completo y correr diffing del Virtual DOM", "Compilar", "El DOM"], 1, "La señal conoce sus consumidores y toca SOLO ese punto del DOM: no hay VDOM, memo ni re-renders."),
 Q("En Solid el componente se ejecuta…", ["En cada cambio", "Una sola vez (setup); luego solo efectos y computados reactivos puntuales", "Nunca", "Por frame"], 1, "Setup único + grafo reactivo: es el modelo mental de las hojas de cálculo, no del re-render.")]),
L("3. Qwik y la resumabilidad: HTML que YA sabe", """La idea radical de Qwik: el estado y las relaciones componente→evento se SERIALIZAN en el HTML en el servidor; el cliente NO re-ejecuta nada al arrancar: "reanuda" (resumes) en vez de "hidratar".

  <button on:click="./click.tsx#handle">+</button>   ← el HTML lleva la dirección del handler

Cuando clickeás RECIÉN AHÍ se descarga ese pedacito de código (lazy agresivo, por interacción). Arranque = 0 KB de JS ejecutado. El TTI es instantáneo, en pantallas enormes también.

El operador $: marca puntos de reanudación.
  const onClick = $(() => count.value++);
  const doblado = useComputed$(() => count.value * 2);
El bundler corta tu componente en "closures" cargables a demanda. Escribís componente normal; Qwik lo hace perezoso automáticamente.

Prefetch inteligente: mientras el usuario navega, en idle el service worker pre-descarga los handlers probables (los tocaseables visibles primero) — cuando clickea, ya está.

Cuándo brilla: páginas GRANDES con poca interactividad inicial (ecommerce, contenido, docs, formularios largos): exactamente donde hydration dolía más. El trade: mentalidad nueva (todo serializable: nada de clases/Map/cerraduras no serializables — el linter te guía).""",
[Q("La diferencia resumibilidad vs hidratación es…", ["Son iguales", "El cliente NO re-ejecuta componentes: reanuda desde estado serializado en el HTML", "Menos HTML", "Más JSON"], 1, "Cero trabajo de arranque: el estado vive serializado en el markup y los handlers se cargan bajo interacción."),
 Q("¿Para qué sirve el operador $ en Qwik?", ["JQuery retro", "Marcar puntos de reanudación: el bundler corta ahí para lazy-load fino", "Decoradores CSS", "Debug"], 1, "Es la señal de corte: convierte tu código en fragmentos cargables solo cuando la interacción lo pide.")]),
L("4. Qwik City y SolidStart: full-stack de la nueva ola", """Los metaframeworks llevan estas ideas a apps completas:

QWIK CITY (el "Next.js de Qwik"):
  • File-based routing en src/routes/
  • routeLoader$() (datos en servidor, tipo getServerSideProps pero streaming)
  • routeAction$() (mutations/progressiva sin JS del cliente — funciona aunque JS no cargue; con JS se vuelve SPA-feeling)
  • Adapter: Node, Cloudflare, Netlify, Vercel, Deno

SOLIDSTART:
  • Misma família sobre Solid: señales + islas + streaming
  • Una de las experiencias de DX más elogiadas post-2024

El mercado de verdad:
  React+Next sigue dominando empleos (network effect). Vue+Nuxt es el segundo amor. Angular rebotó con sus propias señales (¡validaron el modelo!). Svelte 5 adoptó "runes" (¡también señales!).

La lección profunda NO es "usá Qwik": es que las SEÑALES ganaron la guerra de ideas — todos los frameworks grandes convergen a reactividad fina. Aprender el modelo (signal → memo → effect) hoy es aprender el React del 2027. Los sintaxis cambian; el grafo reactivo queda.""",
[Q("¿Qué valida que Angular y Svelte 5 hayan adoptado señales?", ["Que copian a Solid", "Que la reactividad fina ganó la guerra de ideas: converge toda la industria", "Que React murió", "Nada relevante"], 1, "Cuando los grandes copian un modelo, el conocimiento del MODELO (no la sintaxis) es la inversión segura."),
 Q("El routeAction$ de Qwik City destaca por…", ["Solo funcionar con JS", "Funcionar como mutation progresivo aunque JS del cliente todavía no cargó", "Usar GraphQL", "Ser lento"], 1, "Enhancement progresivo real: la acción funciona en la petición HTML base y se siente SPA cuando JS llega — robustez first.")]),
L("5. Islas y la composición con Astro (este mismo stack)", """Astro es el "pegamento" agnóstico: renderiza TODO a HTML estático por defecto y abre "islas" de interactividad donde haga falta — incluso de frameworks DISTINTOS en una misma página:

  <MenuReact client:visible />
  <CarritoSolid client:load />
  <BusquedaVue client:idle />

Directivas de hidratación granulares (solo esa isla descarga JS y solo cuando):
  client:load → al cargar
  client:visible → cuando entra al viewport (¡footer interactivo no cuesta arriba!)
  client:idle → en tiempo muerto del navegador
  client:only="react" → solo cliente (salta el SSR de esa isla)

Esta plataforma ES Astro con islands de script vanilla (el chat, pomo, lab): HTML estático barato en el CDN + interactividad óa demanda, sin framework de 100 KB.

El patrón recomendado de arquitectura 2026:
  contenido (posts, docs, landings)         → HTML puro Astro
  interactividad chica (contador, menú)     → isla vanilla o Alpine
  componente caliente (editor, dashboard)   → isla Solid/Qwik/React donde corresponde
  migración gradual desde SPA               → Astro acepta el componente React viejo como isla

Gana porque separa PAGAR (JS, complejidad) de VALOR (interactividad real).""",
[Q("¿Qué hace client:visible en una isla Astro?", ["La oculta", "Difiere la carga de su JS hasta que el elemento entra al viewport", "La imprime", "La cachea"], 1, "El JS de un widget del footer no debería bloquear el arranque: se carga solo si el usuario llega a verlo."),
 Q("Para migrar una SPA React vieja gradualmente, Astro permite…", ["Borrarla", "Meter los componentes React viejos como islas mientras el resto pasa a HTML estático", "Nada, rewrite", "Solo con Qwik"], 1, "Las islas destraban migraciones: convivencia framework-por-componente en la misma página, sin big-bang rewrite.")]),
L("6. Decidir en 2026: el árbol de decisión honesto", """Pregunta 1: ¿Qué dominio?
  Trabajo/empresa conservadora, equipo grande → REACT (empleo, ecosistema, librerías, soporte: no te vas a arrepentir del default).
  Contenido/marketing/docs/ecommerce       → ASTRO/páginas estáticas + islas ligeras (SEO y TTI primero).
  Dashboards intensos en interactividad    → React/Solid/Vue con Vite — y Solid si el equipo admite lo nuevo.
  Startup performance-obsesiva con audiencia móvil emergente → Qwik (TTI es ventaja de negocio).
  Meta: aprender el modelo del futuro      → SOLID + SIGNALS (la idea, no la marca).

Pregunta 2: ¿qué métrica cuida tu producto?
  Conversión móvil/SEO → tiempo-a-interactivo = vida: islas + poco JS.
  Productividad del equipo a 5 años → madurez de ecosistema: React/Vue.
  Retención de devs felices → la DX que ame tu equipo (medible: tiempo hasta primer PR productivo).

Pregunta 3: ¿reescribir? CASI NUNCA. Se migra por islas o por rutas; el big-bang rewrite mata productos (historia demostrada).

Y la Regla Final: el framework dura 3-5 años; el MODELO mental dura 20. Señales, islas, SSR-streaming y resumabilidad son el frontend post-2026: aprendé ideas y la sintaxis sale sola después.""",
[Q("Vas a un equipo grande en banca. ¿Framework sensato?", ["Qwik por hype", "React: empleo, ecosistema, librerías probadas — el default no se discute ahí", "Vanilla", "Elm"], 1, "En contexto conservador importan contratación y ecosistema maduro más que el mejor TTI teórico."),
 Q("¿Cuál es la tesis central sobre aprendizaje duradero de frontend?", ["Aprender la última marca", "Las sintaxis rotan; los modelos (señales, islas, SSR) duran décadas", "Memorizar APIs", "Un solo lenguaje"], 1, "Señales es la idea que ya está en Angular/Svelte/Vue/Solid: invertir en modelos te vuelve multilingüe de frameworks.")])]},
{"slug": "55-ingenieria-de-datos-moderna", "free": False, "n": "🛢️ Ingeniería de Datos Moderna — DuckDB, dbt y ELT", "lecciones": [
L("1. De ETL a ELT: el flip que lo cambió todo", """ETL clásico (1990-2015): Extraer → Transformar (limpiar antes) → Cargar datos YA listos al warehouse. ¿Problema? Necesitás saber CÓMO vas a usar los datos ANTES de guardarlos. Si el negocio pregunta algo nuevo: re-procesar todo.

ELT moderno: Extraer → Cargar RAW (crudo, barato) → Transformar DENTRO del warehouse con SQL, bajo demanda y con versionado. La base analítica moderna es tan rápida que transformar adentro cuesta centavos; las fotos crudas quedan para siempre (reprocesar es gratis).

El stack moderno 2026 ("post-Spark" para el 90% de equipos):
  Ingesta:    APIs/CSV/db replicas → Airbyte/Fivetran (o tu script)
  Storage:    Parquet en object storage (o directo en Postgres si es chico)
  Motor:      DuckDB (OLAP en tu laptop/VPS, gratis, local) o BigQuery/Snowflake
  Transform:  dbt (SQL + tests + docs + linaje)
  BI:         Metabase/Superset/Lightdash

El insight clave: el 90% de las empresas NO tiene "big data" (tienen gigabytes, no petabytes). Para gigabytes, el stack de tus sueños corre en tu laptop o en un VPS de U$S 5: por eso DuckDB explotó — es "el SQLite de los datos analíticos".""",
[Q("¿Cuál es la diferencia práctica central de ELT frente a ETL?", ["Las letras", "Primero cargás crudo y transformás DESPUÉS dentro del warehouse: no necesitás conocer el uso al guardar", "Es solo marketing", "Usa Python"], 1, "Con los datos crudos siempre disponibles, nuevas preguntas del negocio = nuevo modelo SQL, no re-procesar todo el pipeline."),
 Q("¿Por qué DuckDB le quita trabajo a Spark en la mayoría de los casos?", ["Spark murió", "La mayoría de los datasets caben en una laptop/VPS; no necesitás un cluster distribuido", "Es gratis", "Corre en navegador solamente"], 1, "Si tus datos son GB, un motor columar local (DuckDB) los procesa más rápido y barato que un cluster coordinando máquinas.")]),
L("2. DuckDB: SQL analítico sin infraestructura", """DuckDB es OLAP embebido: una sola librería/binario, dentro de tu proceso (Python, R, JS, CLI), que lee datos COLUMNAR (rápido en agregaciones) y archivos modernos directamente:

  pip install duckdb

  import duckdb
  duckdb.sql(\"\"\"
    SELECT pais, count(*) usuarios, sum(monto) ingresos
    FROM 'ventas.parquet'              -- ¡lee parquet directo!
    WHERE fecha >= '2026-01-01'
    GROUP BY pais ORDER BY ingresos DESC
  \"\"\").df()                            -- → DataFrame de pandas

También lee CSV gigante (más rápido que pandas), JSON anidado, y hasta Postgres:
  ATTACH 'dbname=tienda user=ana' AS pg (TYPE POSTGRES);
  SELECT * FROM pg.orders LIMIT 10;    -- federado: cruza archivos y bases

Por qué vuela: VECTORIZADO (procesa por lotes columnares, como Numpy) + columnar (lee solo las columnas del SELECT: tu CSV de 40 columnas y 5 consultadas = lee ~12% del disco).

Casos de oro:
  • EDA local de CSV de 10 GB que Excel ni abre
  • "dbt + duckdb": el data warehouse de bolsillo (dev y CI gratis)
  • Backend analítico de un SaaS chico sin pagar Snowflake
  • MotherDuck: su SaaS (DuckDB en la nube colaborativo, si algún día hace falta)""",
[Q("¿Por qué leer solo las columnas del SELECT acelera todo en DuckDB?", ["Lee menos disco: en formato columnar las columnas no usadas ni se descomprimen", "Es magia", "Usa GPU", "Tiene cache"], 0, "Formato columnar: si tu tabla tiene 40 columnas y tu query usa 5, el ~87% del disco jamás se toca."),
 Q("DuckDB puede consultar datos de…", ["Solo CSV", "Parquet, CSV, JSON y hasta Postgres federado, todo con el mismo SQL", "Solo su formato", "Solo MySQL"], 1, "Su superpoder federado: un JOIN entre un CSV local, un parquet en S3 y tu Postgres — sin montar infraestructura.")]),
L("3. dbt: el SQL crece (tests, docs, linaje)", """dbt (data build tool) es ingeniería de software aplicada al SQL: convierte transformaciones en MODELOS versionados con tests y documentación automática.

  -- models/ingresos_por_pais.sql
  SELECT pais, sum(monto) AS ingresos
  FROM {{ ref('stg_ventas') }}
  GROUP BY pais

  {{ ref() }} = grafo de dependencias AUTOMÁTICO: dbt sabe qué construir y en qué orden (DAG visual gratuito: docs/linaje de dónde viene cada columna — auditoría feliz).

  -- schema.yml
  models:
    - name: ingresos_por_pais
      tests:
        - dbt_utils.unique_combination_of_columns: { columns: [pais] }
      columns:
        - name: ingresos
          tests: [not_null]

  dbt run   → compila y ejecuta el DAG
  dbt test  → valida calidad de datos (¡tests de DATOS, no de código!)

Tests de datos salvadores: uniqueness en PK, not_null en montos, accepted_values (status IN ('paid','pending')), relaciones (todo user_id existe en users). Antes se descubría el dato sucio en el dashboard del CEO; ahora falla el pipeline con alerta.

El flujo profesional: PR con modelo nuevo → CI corre dbt test → merge → deploy. SQL tratado como código serio: porque LO ES.

(dbto Funciona con DuckDB local: pipeline profesional completo en tu máquina a costo cero.)""",
[Q("¿Qué aporta {{ ref('modelo') }} en dbt?", ["Nada, es decorativo", "Construye el DAG de dependencias: orden de ejecución y linaje automático", "Es más rápido", "Hace backup"], 1, "Grafo declarativo: dbt sabe qué tabla depende de cuál, las corre en orden y te dibuja el linaje columna por columna."),
 Q("El test de datos 'accepted_values' en la columna status previene…", ["Queries lentos", "Valores inesperados ('paidd') rompiendo dashboards en producción", "SQL injection", "El huevo de pascua"], 1, "La calidad se valida en el pipeline, no en la presentación al CEO: tests de datos = tests unitarios del pipeline.")]),
L("4. Formatos de datos: CSV vs JSON vs Parquet", """El formato define velocidad, tamaño y quién puede leerlo — decisión de ingeniería, no de gusto.

CSV: filas de texto separadas por coma.
  ✔ humano-legible, universal ✘ sin tipos (fecha como string), lento, sin compresión real, se rompe con comas/comillas.
  ✔ PARA: intercambio chico con humanos, exports de negocio.

JSON: semi-estructurado.
  ✔ anidado natural, ✘ verboso, sin schema, lento en volumen.
  ✔ PARA: APIs, documentos, configs. NDJSON (una línea por registro) para streams y logs.

PARQUET: columnar binario comprimido (el estándar analítico):
  ✔ ×3-10 más chico (compresión por columna: todos los 'pais' juntos comprimen divino)
  ✔ con tipos y schema embebidos, ✔ lectura columnar (solo lo del SELECT)
  ✘ no es humano-legible ni streamable
  ✔ PARA: data lakes, analytics, archivado. DuckDB/Spark/BigQuery lo leen nativo.

ARROW (intercambio en MEMORIA columnar): parquet en disco ↔ arrow en RAM: zero-copy entre Python/R/JS/DuckDB.

Regla rápida del stack moderno:
  los datos transitan JSON (APIs) → se archivan en PARQUET (lake) → se calculan en ARROW (RAM) → se entregan al humano en CSV/HTML. 4 formatos, 1 día de trabajo.""",
[Q("¿Por qué un parquet pesa 5-10× menos que el CSV del mismo dato?", ["Es mentira", "Comprime por columna: valores similares juntos comprimen muchísimo mejor", "Borra columnas", "Es bin"], 1, "Todos los 'UY' de la columna país juntos → RLE los colapsa; en CSV cada fila repite el texto completo al azar."),
 Q("Arrow resuelve…", ["El disco", "Intercambio entre herramientas en RAM sin copiar: zero-copy Python↔DuckDB↔BI", "Parquet roto", "APIs lentas"], 1, "La fricción entre librerías era serializar/deserializar de a millón rows: Arrow es memoria columnar compartida estándar.")]),
L("5. Pipelines confiables: idempotencia, incremental y backfill", """La diferencia entre un pipeline de juguete y uno profesional NO es la velocidad: es QUE PODÉS RE-CORRERLO SIN MIEDO.

IDEMPOTENCIA: correrlo 2 veces = mismo resultado que 1.
  ✘ INSERT INTO ventas SELECT * FROM api(...)   → duplicás datos al reintentar tras un fallo
  ✔ MERGE/upsert por clave natural (order_id), o particiones replace: DELETE del día + INSERT del día.

  -- patrón partición reemplazable
  DELETE FROM ventas WHERE fecha = '2026-09-21';
  INSERT INTO ventas SELECT * FROM raw WHERE fecha = '2026-09-21';

INCREMENTAL: procesar solo lo nuevo (tabla enorme: no re-proceses 5 años cada noche).
  WHERE actualizado > (SELECT max(actualizado) FROM destino)

BACKFILL: re-correr hacia atráspor rango de fechas (bug encontrado en marzo: re-corrés ene-mar de forma controlada, en particiones).

ORQUESTADORES (el despertador con memoria): Airflow (el clásico pesado), Dagster/Prefect (los modernos, DX mucho mejor, testing integrada), o cron + disciplina para proyectos chicos. Qué aportan: calendario de corridas, reintentos con backoff, dependencias entre tasks, alertas, backfill con parámetros.

Antipatrones que cobran factura:
  • pipelines que solo funcionan si no fallan (sin idempotencia)
  • horarios solapados (el task de ayer aún corre cuando empieza el de hoy)
  • alertas que gritan todo el día → se ignoran → cuando falla de verdad nadie mira""",
[Q("Un pipeline idempotente permite…", ["Correrlo 5 veces seguidas con el mismo resultado, clave tras fallos y reintentos", "Correr más rápido", "No tener tests", "Usar cron"], 0, "Si reintentar duplica datos, nadie se anima a reintentar — y los pipelines fallan SIEMPRE tarde o temprano. Idempotencia = poder re-correr en paz."),
 Q("¿Qué patrón evita re-procesar 5 años de historia cada noche?", ["Borrar la historia", "Incremental: WHERE actualizado > max(destino), solo lo nuevo", "Más servidores", "Parquet"], 1, "El merge incremental por watermark es el estándar para tablas grandes — complementado con backfill por particiones cuando hay que arreglar historia.")]),
L("6. Calidad y gobernanza mínima (que protege tu noche)", """La gobernanza son reglas acordadas para no despertar a las 3 AM por datos rotos ni para auditar un breach.

CONTRATOS DE DATOS: el productor (la API, el equipo de ventas) firma: "esta tabla tendrá ESTAS columnas, tipos y reglas; los cambios se avisan". Se valida en el pipeline (schema check automático al llegar el dato: si eliminaron la columna email → pipeline falla AHÍ, no en el dashboard de mañana).

PII (datos personales): regla de 3 líneas de defensa:
  1. No guardar lo que no necesitás (la mejor seguridad)
  2. Hash/enmascarar en staging (email → sha256 para joins, mostrar a***@x.com)
  3. Acceso por rol + log de quién miró qué (GDPR/CCPA lo exigen)

Linaje mínimo gratis: dbt docs → diagrama fuente→tabla→dashboard. Cuando cambiás 'usuarios.nombre' sabés QUÉ rompés antes de romperlo.

Catálogo de preguntas que un buen equipo responde en 5 min:
  ¿De dónde viene este número del dashboard?              → linaje
  ¿Quién puede ver el sueldo en la tabla de empleados?    → acceso/roles
  ¿Desde cuándo está roto el campo edad?                  → tests + alertas
  ¿Qué pasa si borro esta columna?                        → dependencias del DAG

La frase que resume todo: trust de datos = tests + linaje + contratos + acceso mínimo. Sin eso, cada dashboard es una hipótesis bonita.""",
[Q("Un contrato de datos evita principalmente…", ["Reuniones", "Que un cambio del productor rompa en silencio el consumo: se detecta en el pipeline con schema check", "Los JOINs", "El GDPR"], 1, "Sin contrato, cuando quitan la columna email te enterás con el dashboard roto a las 9 AM; con contrato, el pipeline falla en el punto exacto y hora exacta."),
 Q("La primera línea de defensa con datos personales (PII) es…", ["Encriptarlos todos", "NO guardar lo que no necesitás: lo no almacenado no se filtra", "Ocultar la columna", "VPN"], 1, "Data minimization: es la única protección infalible — cada campo sensible que guardás es una deuda de riesgo.")])]},
]

print("✔ cursos_nuevos_data3 cargado:", len(NUEVOS), "cursos")
