// 🤖 POST /api/chat — Tutor IA con Workers AI + RAG de respaldo de la propia currícula
import type { APIRoute } from 'astro';

export const prerender = false;

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type, X-Token',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
};
export const OPTIONS: APIRoute = () => new Response(null, { status: 204, headers: CORS });
const J = (d: unknown, status = 200) => Response.json(d, { status, headers: CORS });

const stop = new Set('de la el los las un una en por para con sin sobre entre como más mas muy si no al del lo le les su sus tu tus mi mis es son sea ser fue que a o u y e ni ya pero cuando dónde donde cómo cual cuál quien quién hay hacer puedo puede puedes tengo tiene tienen me te se nos'.split(' '));
const toks = (s: string) => s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9+#. ]/g, ' ').split(/\s+/).filter(x => x.length > 1 && !stop.has(x));

async function ragFallback(request: Request, query: string) {
  try {
    const url = new URL('/data/corpus.json', request.url);
    const r = await fetch(url);
    if (!r.ok) return null;
    const corpus = await r.json() as any;
    const q = new Set(toks(query));
    let best: any = null;
    for (const d of corpus.l || []) {
      const words = new Set(toks(String(d.t || '') + ' ' + String(d.c || '') + ' ' + String(d.x || '')));
      let score = 0;
      for (const t of q) if (words.has(t)) score++;
      if (!best || score > best.score) best = { score, d };
    }
    if (!best || best.score < 1) {
      return '🏠 Tutor local: no encontré una coincidencia clara en las 329 lecciones. Probá con el nombre del concepto, lenguaje o curso.';
    }
    return '📖 Tutor de la currícula — «' + String(best.d.t || 'Lección') + '» (' + String(best.d.c || '') + ')\n\n' + String(best.d.x || '').slice(0, 1800);
  } catch {
    return null;
  }
}

export const POST: APIRoute = async ({ request, locals }) => {
  try {
    const body = await request.json() as { messages?: { role: string; content: string }[] };
    if (!Array.isArray(body.messages) || !body.messages.length) return J({ ok: false, error: 'messages requerido' }, 400);
    const messages = body.messages
      .filter(m => ['system', 'user', 'assistant'].includes(m.role) && String(m.content || '').length <= 4000)
      .slice(-20);
    const lastUser = [...messages].reverse().find(m => m.role === 'user')?.content || '';
    const env = (locals as any).runtime?.env;

    if (env?.AI) {
      let lastError = '';
      for (const model of ['@cf/meta/llama-3.3-70b-instruct-fp8-fast', '@cf/meta/llama-3.2-3b-instruct']) {
        try {
          const r: any = await env.AI.run(model, { messages, max_tokens: 900, temperature: 0.35 });
          if (r?.response) return J({ ok: true, respuesta: r.response, backend: 'workers-ai', model });
        } catch (e: any) { lastError = String(e?.message || e); }
      }
      const fallback = await ragFallback(request, lastUser);
      if (fallback) return J({ ok: true, respuesta: fallback, backend: 'local-rag', warning: lastError || 'Workers AI sin respuesta' });
    }

    const fallback = await ragFallback(request, lastUser);
    if (fallback) return J({ ok: true, respuesta: fallback, backend: 'local-rag' });
    return J({ ok: false, error: 'Tutor temporalmente no disponible' }, 503);
  } catch (e: any) {
    return J({ ok: false, error: 'Tutor: ' + String(e?.message || e) }, 500);
  }
};
