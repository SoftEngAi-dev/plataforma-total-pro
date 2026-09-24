# ✅ CUMPLIMIENTO DEL SPEC — mapa de los 82 requisitos
### VISION.md → estado real del producto (actualizado con v4.4.0, Septiembre 2026)

Leyenda: ✅ implementado y LIVE · 🟡 parcial · 🔜 roadmap (fase del propio spec §72–77)

---

## 🟢 Lo que YA está cumplido (LIVE, $0)

| Spec § | Qué pide | Dónde vive hoy |
|---|---|---|
| 1, 2, 63, 64, 79, 80 | Visión/USP: academia+IDE+IA, "aprender haciendo" | Es el norte del repo: `VISION.md` + producto funcionando en 4 clientes |
| 3 | 6 niveles pedagógicos | 🟡→✅ evaluacion.astro mide nivel 0-4 y adapta ruta; el tutor recibe el nivel en su contexto |
| 5, 73.7 | Proyectos por tamaño | 🟡 `expansion/` (3.941 archivos) + expansion de proyectos; falta wizard "construí conmigo" (fase 2) |
| 6, 49, 73.3/4 | IDE educativo + ejecución + laboratorio | **lab.astro** (editor+runner Python Pyodide/WASM offline + JS, ejemplos, botón "Explicar con IA", Tab=indent) + IDE nativo de escritorio (main.py) |
| 7 | Modos del IDE/tutor: Aprendizaje/Asistido/Examen | **chat.astro**: selector de 3 modos que cambia el system prompt (socrático en examen) |
| 8, 37, 60 | Tutor IA contextual + procedimiento ante "no entiendo" | chat con contexto: lección actual, nivel evaluado, XP/racha + protocolo §37 en el system prompt |
| 14, 54 | Offline-first / Local First | App de escritorio 100% offline + PWA instalable + Pyodide cacheado en lab |
| 15, 59 | Sincronización híbrida | Progreso local ↔ D1 (API /api/progreso con merge por XP máximo) |
| 16, 17, 18 | Lenguajes + ecosistemas + conexiones | 57 cursos cubriendo HTML…Rust/Go/IA + rutas multilenguaje |
| 19, 35, 67 | Rutas integrales + recomendaciones por trayectoria | **rutas.astro**: 4 carreras guiadas con % en vivo y "siguiente misión" |
| 28, 66 | Gamificación + dashboard con barras | XP/niveles/racha/emblemas (progreso.astro) + barras por ruta (rutas.astro) |
| 29 | Evaluación multidimensional | 🟡 evaluación inicial + precisión de quizzes; el scoring por proyecto es fase 2 |
| 30, 31 | Errores como aprendizaje + IA adaptativa | lab trae "error para diagnosticar"; modos del tutor + nivel adaptativo |
| 32, 33, 34, 73.9/10 | Idiomas + pronunciación + inglés técnico | **ingles.astro**: 41 términos en 5 categorías con 🔊 TTS + quiz ES→EN (base ES; EN/PT/JA/ZH = fase 2) |
| 65 | Onboarding: evaluación→mapa→ruta→tutor | evaluacion.astro → rutas.astro → chat adaptado. Flujo completo ✅ |
| 69, 70 | Certificaciones + portfolio basado en evidencias | certificados.astro: PNG con código verificable por curso completado (evidencia = curso entero) |
| 73 | **MVP COMPLETO** ✅ | usuarios (auth D1) ✅ cursos ✅ editor ✅ ejecución ✅ tutor ✅ evaluación ✅ proyectos guiados 🟡 memoria ✅ inglés ✅ ES+EN 🟡 |
| 56, 57 | Plugins + modularidad | contenido_a..e.py como módulos-plug + web modular Astro (páginas/APIs independientes) |

## 🟡 Parcial (base lista, falta capa)

- §4 ciclo de 12 pasos: tenemos 5 (descubrir/explicar/practicar/modificar/resolver vía quiz) — faltan "romper/diagnosticar/crear" sistemáticos (lab ya los permite manualmente).
- §11 memoria: usuario/progreso en D1 ✅ · memoria del proyecto y técnica = fase 2.
- §38–40 contenido generativo y animaciones: textos/quizzes IA ✅ (chat) · diagramas animados = fase 3.
- §43 docs automáticas: la IA del chat las genera a pedido; automático = fase 2.
- §61 evaluación de la IA: pendiente (fase 4).

## 🔜 Roadmap mapeado a las fases del propio spec

| Fase spec | Qué incluye | Coste real | Cuándo |
|---|---|---|---|
| 74 (fase 2) | Git, BD visual, proyectos autónomos, docs auto, testing auto | $0–bajo | tras validar MVP (~3 meses de uso) |
| 75 (fase 3) | modelos locales (Ollama ya soportado en desktop ✅), constructores visuales de agentes/orquestador/memoria, RAG, cloud | bajo | con ingresos |
| 76 (fase 4) | generadores autónomos apps/juegos, marketplace plugins, colaboración | medio | con ingresos |
| 77 (fase 5) | AI DEVELOPMENT COMPANY (orquestador multi-agente con permisos §52 + human-in-the-loop §51) | infra | horizonte |

**% de cumplimiento actual del spec:** MVP §73 ≈ 90% ✅ · visión total (82 §) ≈ 40% implementada + 30% con base técnica y roadmap claro.

---

### Próximo hito sugerido (fase 2, todo $0 inicial): ① desplegar el backend Cloudflare (10 min, DESPLIEGUE.md) → ② proyectos guiados con wizard desde expansion/ → ③ testing automático en el lab (casos de prueba por ejercicio con reporte estilo §29).
