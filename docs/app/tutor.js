/* 🏠 PTutor — Motor del "Tutor Propio": 100% nuestro, sin modelos externos.
   Recuperación tipo buscador (TF-IDF s/p) sobre NUESTRA currícula (269 lecciones
   + 538 preguntas de quiz). Corre en el navegador y también en Node (tests). */
(function (global) {
  'use strict';

  // stopwords español (las más comunes, incl. términos de pregunta)
  const STOP = new Set(('de la el los las un una unos unas en por para con sin sobre entre como mas muy si no al del lo le les su sus tu tus mi mis es son sea ser fue fueron está están esta este estos esto eso ese esa esos esas que qué a o u y e ni o ya pero sino cuando cuándo dónde cómo cuál cuáles cuanto cuánto quien quién hay hago hacer puede puedo puedes podemos tiene tienen tengo me te se nos os les yo él ella ellos ellas ustedes vosotros cualquier cualesquier cada tanto tanta otros otras mismos mismas tal tales algo nada poco mucho más menos después antes desde durante mediante según siendo hacia hasta acerca vez veces solo sólo así ahí aquí allí donde dondequiera porque aunque mientras tal cual dicho dicha mismo forma forma0 tiene0'.split(' ')));

  const norm = s => (s || '').toString().toLowerCase()
    .normalize('NFD').replace(/[̀-ͯ]/g, '')          // sin tildes
    .replace(/[^a-z0-9ñ_+#.]/g, ' ')               // conserva c#, c++, .js…
    .replace(/\s+/g, ' ').trim();
  const tokens = s => norm(s).split(' ').filter(w => w.length > 1 && !STOP.has(w));

  let CORPUS = null, DF = null, DOCS = null, QDF = null, QDOCS = null;

  function indexar(corpus) {
    CORPUS = corpus;
    DF = new Map(); DOCS = [];
    for (const [i, d] of corpus.l.entries()) {
      // título ×3 + curso ×4 + contenido ×1 (el curso pesa porque orienta el dominio)
      const toks = [...tokens(d.t), ...tokens(d.t), ...tokens(d.t),
                    ...tokens(d.c), ...tokens(d.c), ...tokens(d.c), ...tokens(d.c), ...tokens(d.x)];
      const tf = new Map();
      for (const t of toks) tf.set(t, (tf.get(t) || 0) + 1);
      DOCS.push(tf);
      for (const t of tf.keys()) DF.set(t, (DF.get(t) || 0) + 1);
    }
    QDF = new Map(); QDOCS = [];
    for (const q of corpus.q) {
      const toks = tokens(q.p);
      const tf = new Map();
      for (const t of toks) tf.set(t, (tf.get(t) || 0) + 1);
      QDOCS.push(tf);
      for (const t of tf.keys()) QDF.set(t, (QDF.get(t) || 0) + 1);
    }
  }

  const buscarTop = (consulta, docs, df, nTotal, k = 3) => {
    const qs = tokens(consulta);
    if (!qs.length) return [];
    const puntos = [];
    for (let i = 0; i < docs.length; i++) {
      let score = 0, hits = 0;
      for (const t of qs) {
        const f = docs[i].get(t) || 0;
        if (!f) continue;
        const idf = Math.log(1 + (nTotal - (df.get(t) || 0) + 0.5) / ((df.get(t) || 0) + 0.5));
        score += idf * (f * 2.2) / (f + 1.2);   // saturación BM25-lite (k1=1.2)
        hits++;
      }
      // premio: cobertura (que aparezcan TODAS las palabras clave)
      if (hits) score *= (hits / qs.length) * 0.6 + 0.4;
      if (score > 0) puntos.push([score, i]);
    }
    return puntos.sort((a, b) => b[0] - a[0]).slice(0, k);
  };

  function extraerSnippet(texto, qs, maxLen = 460) {
    // elige las líneas/oraciones con mayor densidad de términos de la consulta
    const lineas = texto.split(/\n+/).map(s => s.trim()).filter(s => s.length > 40 && !/^[\s━══-]+$/.test(s));
    if (!lineas.length) return texto.slice(0, maxLen);
    const punt = lineas.map((s, i) => {
      const tok = tokens(s);
      let sc = 0;
      for (const t of qs) if (tok.includes(t)) sc += 1;
      if (/^  </.test(s) || /^\s{2,}\S/.test(s)) sc *= 0.4;      // penaliza bloques de código puro
      return [sc / (1 + Math.abs(i - lineas.length / 2) * 0.05), i, s];
    }).sort((a, b) => b[0] - a[0]);
    let out = '', usados = 0;
    for (const [sc, _i, s] of punt) {
      if (sc <= 0 && usados > 0) break;
      if (usados >= 3 || out.length + s.length > maxLen) continue;
      out += (out ? '\n' : '') + s; usados++;
    }
    return out || lineas[0].slice(0, maxLen);
  }

  function responder(pregunta) {
    if (!CORPUS) return { tipo: 'vacio', mensaje: 'Corpus no cargado' };
    const qs = tokens(pregunta);

    // 1) ¿coincide con una PREGUNTA DE QUIZ? → respuesta + explicación directa
    const topQ = buscarTop(pregunta, QDOCS, QDF, CORPUS.q.length, 1);
    const topL = buscarTop(pregunta, DOCS, DF, CORPUS.l.length, 3);
    const mejorL = topL[0], mejorQ = topQ[0];

    if (mejorQ && (!mejorL || mejorQ[0] > mejorL[0] * 1.15) && mejorQ[0] > 2.2) {
      const q = CORPUS.q[mejorQ[1]];
      return {
        tipo: 'quiz', curso: q.c, ci: q.ci, j: q.j, leccion: q.t,
        texto: `🎯 Eso aparece en el quiz de **${q.c}**:\n\n**${q.p}**\n✔ Respuesta: **${q.r}**\n\n💡 ${q.e}`,
      };
    }

    // 2) lección más relevante → snippet + enlace
    if (mejorL && mejorL[0] > 2.0) {
      const d = CORPUS.l[mejorL[1]];
      const otras = topL.slice(1).filter(([s]) => s > mejorL[0] * 0.5)
        .map(([_, i]) => ({ t: CORPUS.l[i].t, c: CORPUS.l[i].c, ci: CORPUS.l[i].ci, j: CORPUS.l[i].j }));
      return {
        tipo: 'leccion', curso: d.c, ci: d.ci, j: d.j, leccion: d.t, otras,
        texto: `📖 En tu currícula — **${d.t}** (${d.c}):\n\n${extraerSnippet(d.x, qs)}`,
      };
    }

    // 3) nada suficiente → guía honesta + temas cercanos por palabra
    const vagos = buscarTop(pregunta.replace(/[¿?]/g, ' '), DOCS, DF, CORPUS.l.length, 3)
      .map(([_, i]) => CORPUS.l[i].t + ' (' + CORPUS.l[i].c + ')');
    return {
      tipo: 'sin_hallazgo',
      texto: `🤔 No encontré eso exactamente en la currícula. Recordá que soy el **tutor local**: respondo desde los 57 cursos y 658 preguntas de Plataforma Total, sin IA externa.\n\n` +
        (vagos.length ? `Lo más cercano que veo:\n• ${vagos.join('\n• ')}\n\n` : '') +
        `Probá con algo como: "qué es una variable", "formularios html", "diferencia entre id y class"… o usá el modo 🤖 IA para preguntas abiertas.`,
    };
  }

  async function cargar(urlCorpus) {
    const r = await fetch(urlCorpus);
    const d = await r.json();
    indexar(d);
    return true;
  }

  const API = { cargar, indexar, responder, _tokens: tokens };
  if (typeof module !== 'undefined' && module.exports) module.exports = API;  // Node (tests)
  else global.PTutor = API;                                                   // navegador
})(typeof window !== 'undefined' ? window : globalThis);
