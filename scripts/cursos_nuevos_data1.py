#!/usr/bin/env python3
"""📚 Expansión 2026: 10 cursos nuevos (matemáticas, lógica y tecnología moderna/emergente).
Fuente única → genera: (1) JSON de cursos web, (2) append a indice.json,
(3) módulo contenido_f.py para la app de escritorio. Idempotente (sobrescribe los suyos)."""
import json, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DATA = RAIZ / "web" / "public" / "data"

Q = lambda p, ops, ok, exp: {"p": p, "ops": ops, "ok": ok, "exp": exp}
L = lambda t, x, q=None: {"t": t, "x": x.strip(), "q": q or []}

NUEVOS = [
{"slug": "48-matematicas-para-programadores", "free": True, "n": "📐 Matemáticas para Programadores — Las que Sí Se Usan", "lecciones": [
L("1. La matemática que SÍ usás (y la que no)", """¿Cuánta matemática necesita un dev? MENOS de la que te dijeron, pero OTRA distinta a la del liceo.

La que aparece TODOS los días:
  • Discreta: índices crecen de a 1, nada de decimales
  • Binario/hex: bytes, colores, permisos, máscaras
  • Lógica booleana: cada if es álgebra de Boole
  • Proporcionalidad: regla de 3 en CSS, precios, fps
  • Complejidad: Big O es matemática aplicada

La que casi NO usás (salvo dominios): derivadas, integrales de cálculo clásico, trigonometría avanzada.

Dominios SÍ exigentes: juegos/3D (vectores, matrices), ML (álgebra lineal + estadística), criptografía (teoría de números), gráficos y audio.

Regla 80/20: con esta materia (6 lecciones) cubrís el 90% de la matemática del dev web/backend. Después se aprende por necesidad del proyecto.""",
[Q("¿Qué rama de la matemática describe mejor los índices de un array?", ["Cálculo infinitesimal", "Matemática discreta", "Geometría euclidiana", "Estadística bayesiana"], 1, "Los índices son números enteros separados: 0, 1, 2… Eso es discreto, no continuo."),
 Q("¿Dónde encontrás matemática aunque escribas 'solo CSS'?", ["En ningún lado", "Probabilidad", "Proporcionalidad y regla de 3 (rem, %, aspect-ratio)", "Derivadas"], 2, "Un rem relativo, un 50% o un aspect-ratio 16/9 son proporciones puras.")]),
L("2. Binario, hexadecimal y máscaras de bits", """Las computadoras cuentan en base 2. Un byte = 8 bits = 0..255.

  0b1010 = 8+2 = 10      # literal binario
  0xFF   = 255           # hexadecimal: cada dígito = 4 bits

¿Por qué hex? Es binario compacto: #FF8000 = rgb(255,128,0). ¡Los colores CSS son bytes en hex!

Operadores de bits (están en todo lenguaje):
  & AND   → flags: permisos & 0b100 == lectura?
  | OR    → activar un flag
  ^ XOR   → toggle / checksums básicos
  << >>   → ×2 y ÷2 rápidos; redes y compresión

  const PERM = { r: 0b100, w: 0b010, x: 0b001 };
  let yo = PERM.r | PERM.w;      // 0b110
  (yo & PERM.w) !== 0            // true → puedo escribir

Casos reales: chmod 755 de Linux (¡son bits!), IPv4/máscaras de red, UUIDs, imágenes, UUIDv7, juegos (estado comprimido en ints).""",
[Q("¿A qué decimal equivale 0xFF?", ["15", "255", "256", "100"], 1, "F=15 y son dos dígitos: 15×16 + 15 = 255. Por eso un canal de color va de 0 a 255."),
 Q("chmod 755 guarda permisos como…", ["Strings 'rwx'", "Bits: r=4, w=2, x=1 combinados con OR", "Números al azar", "Tablas SQL"], 1, "7=rwx(111), 5=r-x(101), 5=r-x(101): tres bytes de 3 bits, máscaras puras.")]),
L("3. Álgebra de todos los días (sí, usás funciones)", """f(x) = 2x es una función. En código:

  const f = x => 2 * x;   // ¡literalmente lo mismo!

Despejar ecuaciones = el 50% de programar:
  precio final = base + base * iva     → despejá base:
  base = final / (1 + iva)

Regla de 3 (la reina del frontend):
  420px ─ 100%
  130px ─  x    → x = 130 * 100 / 420 ≈ 31%

  width: calc(130px * 100% / 420px)   // existe de verdad

Proporcionalidad INVERSA: si 2 workers tardan 10h, 5 tardan 4h (producto constante: w×h=k). Sirve para estimar servidores y costos.

El operador % (módulo) = el truco infinito:
  i % 3        → 0,1,2,0,1,2… patrones cíclicos (carrusel!)
  n % 2 === 0  → par/impar
  (i + 1) % len → índice siguiente que "da la vuelta"

Funciones compuestas = pipe: g(f(x)) → x |> f |> g (JS igual: g(f(x))).""",
[Q("Una columna de 130px sobre un contenedor de 420px es qué ancho en %?", ["30.9%", "13%", "42%", "3.1%"], 0, "Regla de 3: 130×100÷420 ≈ 30,95%. La regla de 3 aparece en TODOS los layouts."),
 Q("Para que un carrusel vuelva al inicio tras la última imagen usás…", ["if larguísimo", "try/catch", "índice = (índice + 1) % total", "recursión"], 2, "El módulo da la vuelta sola: (4+1) % 5 = 0. Patrón cíclico universal.")]),
L("4. Álgebra de Boole: tus ifs son matemática", """George Boole (1854) inventó esto antes de que existieran las computadoras. CADA if que escribiste es suyo.

Tablas de verdad:
  AND: true solo si AMBOS true      A && B
  OR:  true si ALGUNO es true       A || B
  NOT: invierte                     !A

Leyes de De Morgan (¡para refactorizar condiciones reales!):
  !(A && B)  ===  !A || !B
  !(A || B)  ===  !A && !B

Ejemplo real — esto es confuso:
  if (!(edad < 18 || !tieneDoc)) { entrar() }
…con De Morgan se lee claro:
  if (edad >= 18 && tieneDoc) { entrar() }

Short-circuit (cortocircuito): JS no evalúa todo:
  usuario && usuario.nombre     // si no hay usuario, no explota
  valor || "sin definir"        // default exprés — ojo con 0 y "" que son "falsy" (usá ?? para null/undefined)

Truthy/falsy en JS: falsy = false, 0, "", null, undefined, NaN. Todo lo demás es truthy (incluidos [] y {} — ¡trampa clásica!).""",
[Q("Según De Morgan, !(A && B) equivale a…", ["!A && !B", "!A || !B", "A || B", "!(A || B)"], 1, "La negación 'se distribuye' invirtiendo el operador: AND pasa a OR. Refactor clave para ifs legibles."),
 Q("En JS, ¿[] (array vacío) es truthy o falsy?", ["Falsy, como ''", "Truthy — [] y {} siempre son truthy (¡cuidado!)", "Depende del navegador", "Da error de tipo"], 1, "[] y {} son objetos: truthy. Solo false, 0, '', null, undefined y NaN son falsy — bug clásico en validaciones.")]),
L("5. Probabilidad y estadística mínima vital", """La MEDIA miente con valores atípicos:
  sueldos: 1000, 1100, 1200, 1300, 95000  → media 20000 🙄
                                           → mediana 1200 ✔ (el del medio)

Regla práctica: si hay outliers, usá MEDIANA o percentiles.

Percentil p95: el 95% está POR DEBAJO de ese valor.
  latencia p95 = 900 ms → 1 de cada 20 usuarios sufre >900 ms
Las empresas serias miden p95/p99, no promedios.

Varianza/desviación estándar: qué tan dispersos están los datos. Dos APIs con media 100 ms: σ=5 es predecible; σ=200 es una lotería.

Probabilidad aplicada:
  • Test A/B: "el botón verde convirtió 4% vs 3%" — ¿es real o azar? (significancia estadística)
  • Birthday paradox: con 23 personas hay 50% de cumpleaños repetidos → por eso los HASHES colisionan antes de lo que intuís (¡importante en seguridad!)
  • Combinatoria: contraseña de 4 dígitos = 10⁴ = 10.000 opciones; cada carácter extra multiplica el espacio.

Sesgo del superviviente: mirar solo los casos exitosos (startups que vitrina) oculta la base real.""",
[Q("Con outliers (un valor gigante entre muchos normales), ¿qué medida representa mejor al grupo?", ["La media", "La desviación estándar", "La mediana", "El máximo"], 2, "La mediana es robusta: un sueldo de 95.000 no la mueve. La media sí se distorsiona."),
 Q("Tu endpoint tiene p95 = 900 ms. ¿Qué significa?", ["Tarda 900 ms siempre", "El 95% tarda MENOS de 900 ms (1 de 20 sufre más)", "Promedio 900 ms", "El servidor está al 95% de CPU"], 1, "Percentiles: p95 = límite superior del 95% de los casos. Así se mide latencia real en producción.")]),
L("6. Big O: la matemática de ir rápido", """Complejidad = cuántas operaciones hacés según el tamaño n de los datos. Es ÁLGEBRA aplicada:

  O(1)      constante  → acceder array[i], hash lookup
  O(log n)  binaria    → búsqueda binaria: 1.000.000 → 20 pasos
  O(n)      lineal     → recorrer la lista una vez
  O(n log n)           → buenos sorts (mergesort, sort nativo)
  O(n²)     cuadrática → doble for anidado: 10k ítems = 100M ops 🐌
  O(2ⁿ)     exponencial→ fuerza bruta: inusable con n>40

Contá operaciones, no tiempo:
  for x in A:            # O(n)
    for y in B:          # O(n) → total O(n²)
      if x == y: ...

¿Y cuánto es n² en la práctica? n=100.000 → 10.000 MILLONES de comparaciones. Minutos. Con hash (Set) es O(n): milisegundos.

  // antes O(n²)
  const setB = new Set(B);          // O(n) construir
  for (const x of A) if (setB.has(x)) …   // O(n) total ✅

Regla mental: input ×10 → O(n) tarda ×10; O(n²) tarda ×100. Por eso los problemas de escala NO se arreglan con más CPU: se arreglan con mejor matemática.""",
[Q("Búsqueda binaria sobre 1.000.000 de elementos ordenados toma ~…", ["1.000.000 pasos", "500.000 pasos", "20 pasos", "2 pasos"], 2, "log₂(1.000.000) ≈ 20: cada paso parte a la mitad. Es el superpoder de O(log n)."),
 Q("Vas a buscar coincidencias entre dos listas de 100k ítems. ¿Mejor plan?", ["Doble for (simple y honesto)", "Meter una lista en un Set y recorrer la otra: O(n)", "Sort de ambas y fe ciega", "Base de datos sí o sí"], 1, "El doble for es O(n²)=10⁴ millones de ops. El Set convierte a O(n): la diferencia entre minutos y milisegundos.")])]},
{"slug": "49-logica-y-pensamiento-computacional", "free": True, "n": "🧠 Lógica y Pensamiento Computacional", "lecciones": [
L("1. Pensar como una computadora (sin ser una)", """El pensamiento computacional tiene 4 pilares — los usás aunque no los nombres:

1️⃣ DESCOMPOSICIÓN: problemón → problemas chicos.
   "Hacer un e-commerce" → catálogo + carrito + pagos + envíos + auth… y cada uno se subdivide.

2️⃣ RECONOCIMIENTO DE PATRONES: "esto se parece a aquello".
   Un carrusel, un menú móvil y un lightbox son LO MISMO: estado abierto/cerrado + click.

3️⃣ ABSTRACCIÓN: ignorar el detalle, quedarse con la interfaz.
   No necesitás saber cómo funciona fetch por dentro: sabés qué entra (url) y qué sale (promesa de response).

4️⃣ ALGORITMOS: pasos precisos, sin ambigüedad.
   La computadora no "se da cuenta": "agregale sal" no existe; "agregar 5 g de NaCl" sí.

Ejercicio mental: describí cómo cruzar la calle con pasos tan precisos que los pueda seguir un robot. Vas a notar CUÁNTAS decisiones implícitas das por sentadas (¿qué tan rápido viene ese auto?).

Esa sensibilidad — nada queda implícito — ES programar.""",
[Q("Convertir 'hacer una red social' en auth + perfiles + feed + mensajería es…", ["Abstracción", "Descomposición", "Deducción", "Refactorización"], 1, "Dividir el problemón en partes manejables: el primer pilar del pensamiento computacional."),
 Q("Notar que un carrusel y un menú hamburguesa comparten estado abierto/cerrado es…", ["Reconocer patrones", "Descomponer", "Encapsular", "Optimizar"], 0, "Ver la misma estructura en problemas distintos: así nacen las librerías y los componentes reutilizables.")]),
L("2. Lógica proposicional: los átomos del razonamiento", """Una PROPOSICIÓN es algo que es verdadero o falso: "servidor responde", "edad ≥ 18". No lo son: "cerrá la puerta" (orden), "¿qué hora es?" (pregunta).

Conectivos:
  A ∧ B  conjunción (AND)
  A ∨ B  disyunción (OR — ¡inclusivo! "¿café o té?" puede ser ambos)
  ¬A     negación
  A → B  implicación (si A entonces B)

La trampa TEÓRICA #1 del mundo: confundir A→B con B→A (el converso).
  "Si llueve, la calle se moja"  NO implica  "si la calle está mojada, llovió"
  (pudo pasar un camión de limpieza)

En debugging esto es ORO:
  "Si hay bug de permisos, falla el login" ≠ "si falla el login, es permisos"
  El login falla por 20 causas. No saltés a la primera.

Contrarrecíproco (SÍ equivale): A→B ⇔ ¬B→¬A
  "si loguea, tiene token" ⇔ "si no tiene token, no loguea" — útil para descartar: buscá el token PRIMERO.

Condición necesaria vs suficiente:
  • Tener licencia es NECESARIO para manejar (sin ella no), pero no SUFICIENTE (hay que saber manejar).
  • En código: token válido es necesario para /api/progreso; no suficiente (el servidor puede caer).""",
[Q("«Si está mojado, llovió» falla como razonamiento porque…", ["La lluvia no moja", "Confunde A→B con su converso B→A", "Usa OR exclusivo", "Es una tautología"], 1, "'Si llueve, se moja' no prueba que lo mojado sea lluvia. El error de diagnóstico más común en debugging y en la vida."),
 Q("Token válido es condición NECESARIA para entrar. Si el token es válido y aún así no entrás…", ["Contradicción lógica imposible", "Necesaria no es suficiente: falta otra cosa (servidor caído, permisos, red)", "El token miente", "Es cortocircuito"], 1, "Necesario = sin eso no hay caso, pero con eso no basta. Separar necesario/suficiente salva horas de diagnóstico.")]),
L("3. Tablas de verdad aplicadas a ifs reales", """Toda condición compleja se puede TABULAR y simplificar. Ejemplo real: banner visible si

  esPro || (esTrial && !expiró) || admin

  esPro  trial  !exp  admin  → banner
    1     x     x     x     → 1   (PRO siempre ve)
    0     1     1     x     → 1
    0     1     0     x     → 0   (trial vencido)
    0     0     x     1     → 1   (admin siempre)
    0     0     x     0     → 0

Con la tabla completa (2ⁿ filas, n=variables — acá 8) verificás TODOS los casos, no solo los que se te ocurrieron. Eso es cobertura lógica y es lo que un buen test hace.

Simplificación por agrupación (Karnough mental):
  admin aparece en toda la expresión como OR aparte → no toca el resto.
  esPro idem → la lógica real queda: admin || esPro || (trial && !exp).

Chequeo de ifs anidados con De Morgan:
  if (!(a && b)) → equivale a if (!a || !b) → a veces se lee mejor como "guard clauses":
  if (!a) return; if (!b) return; // camino feliz abajo, sin anidar

Regla del equipo sano: la condición la escribe una persona a las 23:00; la tabla la lee otra a las 09:00 en incidente. Las tablas no se cansan.""",
[Q("¿Cuántas filas tiene la tabla de verdad completa de 4 variables?", ["4", "8", "16", "64"], 2, "2ⁿ: cada variable duplica. 2⁴=16 filas cubren TODA combinación posible — cobertura total."),
 Q("Mejor forma de leer if (!(a && b)) {…}", ["if (a && !b)", "if (!a || !b) o guards: if(!a) return; if(!b) return;", "if (!(a) && !(b))", "if (a or !b)"], 1, "De Morgan: ¬(A∧B) = ¬A∨¬B. Los guard clauses dejan el camino feliz plano y legible.")]),
L("4. Cuantificadores: ∀ y ∃ que ya programás", """Lógica de predicados: proposiciones CON variables sobre un dominio ("todos los usuarios", "algún error").

  ∀x: P(x)   "para TODO x vale P"   → JS: array.every(P)
  ∃x: P(x)   "EXISTE algún x con P" → JS: array.some(P)

  emails.every(e => e.includes('@'))   // ∀: todos válidos?
  logs.some(l => l.nivel === 'ERROR')  // ∃: hubo algún error?

Negación de cuantificadores (otro De Morgan, clave en tests):
  ¬(∀x: P) ⇔ ∃x: ¬P   "NO todos cumplen" = "existe uno que NO cumple"
  ¬(∃x: P) ⇔ ∀x: ¬P   "no existe ninguno" = "todos fallan P"

Contraejemplo: para refutar un ∀ alcanza UN caso:
  "todo usuario tiene alias" → encontrás uno sin alias → hipótesis muerta.
  Por eso un solo bug report serio tumba "nunca pasa".

INVARIANTE de bucle: propiedad que vale ANTES y DESPUÉS de cada iteración.
  let total = 0;                       // total = suma de lo procesado
  for (const p of items) total += p.precio;
  // invariante: total siempre es la suma parcial → al salir: suma TOTAL ✔

Los bugs de bucle (off-by-one, acumuladores mal reseteados) son invariantes rotos. Escribir el invariante en un comentario es documentación de élite.""",
[Q("«No todos los tests pasaron» en términos lógicos es…", ["∀ tests: pasan", "¬∃ test que pase", "∃ test que NO pasó", "∀ tests: fallan"], 2, "¬(∀: pasan) ⇔ ∃: ¬pasan. No es lo mismo 'fallaron todos' que 'falló alguno' — y a veces se lee mal el reporte."),
 Q("Para refutar «todos los usuarios activos tienen alias» alcanza con…", ["Probar 100 casos", "Un solo contraejemplo", "La mediana de usuarios", "Un test de estrés"], 1, "Un ∀ se mata con UN contraejemplo. Por eso un solo usuario sin alias obliga a arreglar la migración.")]),
L("5. Dry run e invariantes: pensar el código antes de correrlo", """Los seniors ejecutan el código EN LA CABEZA antes de apretar ▶. Se llama dry run (corrida en seco): tabla de variables paso a paso.

  i = 0; total = 0
  while (i < 3) { total += arr[i]; i++ }   // arr = [10, 20, 30]

  pasada  i  total      condición
   inicio 0    0
     1    0→1  0→10     0<3 ✔
     2    1→2 10→30     1<3 ✔
     3    2→3 30→60     2<3 ✔
     —    3   60        3<3 ✘ sale

Con errores deliberados descubrís:
  • Off-by-one: ¿arranca en 0 o 1? ¿< o <=?
  • Acumulador sin resetear entre llamadas (estado que "gotea" entre tests)
  • Condición de salida que jamás se cumple (while(true) accidental)

Método casos borde — SIEMPRE probá mentalmente:
  lista VACÍA      → ¿devuelve algo razonable?
  UN elemento      → ¿el bucle entra bien?
  el PRIMERO y el ÚLTIMO
  valores NEGATIVOS, cero, null
El 80% de los bugs vive en los bordes, no en el medio.

Precondición/postcondición: qué asumo al entrar ("lista ordenada") y qué garantizo al salir ("total ≥ 0"). Escribirlas evita que otro (o vos en 3 meses) llame mal a tu función.""",
[Q("¿Qué es un dry run?", ["Ejecutar sin guardar", "Simular la ejecución a mano, tabulando variables paso a paso", "Correr sin internet", "Un test de carga"], 1, "La corrida en seco: papel (o cabeza) + tabla de variables. Detecta off-by-one sin compilar nada."),
 Q("¿Dónde se concentra la mayoría de los bugs lógicos?", ["En el centro del array", "En los bordes: vacío, primero, último, cero, negativos, null", "En los comentarios", "En el else implícito"], 1, "Los casos borde rompen supuestos implícitos. Probar mentalmente esos casos primero es la técnica más barata que existe.")]),
L("6. Falacias para debuggear la realidad", """El debugging es ciencia aplicada: hipótesis → experimento → conclusión. Estas falacias arruinan el proceso:

🎯 CONFIRMACIÓN: buscar solo evidencia de tu teoría favorita.
   "Es la base de datos" → mirás solo la DB → 3 horas perdidas y era DNS.
   Antídoto: preguntate qué evidencia te probaría EQUIVOCADO y buscá eso primero.

📊 CORRELACIÓN ≠ CAUSA: "los bugs aumentan los lunes" — ¿causa? ¿o los deploys son los lunes?
   Helados y ahogados suben juntos: la causa tercera es el calor.

🐤 Post hoc ergo propter hoc: "después del cambio X falló" → sí pista, no prueba. Pudo coincidir con pico de tráfico.

✂️ SESGO DEL SUPERVIVIENTE: copiar SOLO lo que hacen los exitosos.
   "Google usa microservicios" → vos tenés 3 usuarios. No ves los miles que murieron con microservicios.

🪓 Navaja de Ockham: la explicación más simple suele ser la correcta.
   Antes de "race condition en el ORM": ¿imprimiste la query real?

Método científico de debug (bisect):
  1. Reproducí el fallo SIEMPRE (si es intermitente, primero hacelo determinista)
  2. Hipótesis falsable: "si comento la línea 42, desaparece"
  3. Experimento mínimo (git bisect = navaja automática: O(log n) commits)
  4. Si se descarta: siguiente hipótesis. NUNCA dos cambios a la vez.

Y la goma de pato: explicar el código en voz alta revela el 50% de los bugs solos.""",
[Q("«Aumentaron los errores tras el deploy del viernes» prueba que el deploy fue la causa…", ["Totalmente cierto", "Es una pista, no prueba: post hoc ≠ causa; pudo ser tráfico o un tercero", "Falso siempre", "Solo si hay logs"], 1, "La correlación temporal orienta la hipótesis pero hay que VERIFICAR con rollback, métricas o reproducción."),
 Q("git bisect encuentra el commit culpable en ~…", ["O(n)", "O(n²)", "O(log n) — búsqueda binaria entre commits", "O(1)"], 2, "Bisecar = partir el rango a la mitad cada vez: 1000 commits → ~10 builds. El método científico con pilas automáticas.")])]},
]

print("✔ cursos_nuevos_data1 cargado:", len(NUEVOS), "cursos")
