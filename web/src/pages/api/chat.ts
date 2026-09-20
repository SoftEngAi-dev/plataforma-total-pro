// 🤖 POST /api/chat — Tutor IA via Cloudflare Workers AI (tier gratis)
import type { APIRoute } from 'astro';

export const prerender = false;

// CORS: permite que la web estática (GitHub Pages) consuma este backend
const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type, X-Token',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
};
export const OPTIONS: APIRoute = () => new Response(null, { status: 204, headers: CORS });
const J = (d: unknown, status = 200) => Response.json(d, { status, headers: CORS });

export const POST: APIRoute = async ({ request, locals }) => {
  try {
    const { messages } = await request.json() as { messages: { role: string; content: string }[] };
    if (!Array.isArray(messages) || !messages.length) {
      return J({ error: 'messages requerido' }, 400);
    }
    const env = (locals as any).runtime?.env;
    if (!env?.AI) return J({ error: 'Workers AI no vinculado (binding [ai] en wrangler.toml)' }, 503);
    const limpios = messages
      .filter(m => ['system', 'user', 'assistant'].includes(m.role) && String(m.content).length < 4000)
      .slice(-20);
    // Catálogo 2026: 3.1-8b deprecado → 3.3-70b primario, 3.2-3b de respaldo
    let r: any = null, err: any = null;
    for (const m of ['@cf/meta/llama-3.3-70b-instruct-fp8-fast', '@cf/meta/llama-3.2-3b-instruct']) {
      try {
        r = await env.AI.run(m, { messages: limpios, max_tokens: 900, temperature: 0.35 });
        if (r?.response) break;
      } catch (e: any) { err = e; }
    }
    if (!r?.response) throw (err || new Error('sin respuesta del modelo'));
    return J({ respuesta: r.response });
  } catch (e: any) {
    return J({ error: 'Tutor ocupado: ' + (e?.message || e) }, 500);
  }
};
