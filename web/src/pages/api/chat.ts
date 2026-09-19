// 🤖 POST /api/chat — Tutor IA via Cloudflare Workers AI (tier gratis)
import type { APIRoute } from 'astro';

export const prerender = false;

export const POST: APIRoute = async ({ request, locals }) => {
  try {
    const { messages } = await request.json() as { messages: { role: string; content: string }[] };
    if (!Array.isArray(messages) || !messages.length) {
      return Response.json({ error: 'messages requerido' }, { status: 400 });
    }
    const env = (locals as any).runtime?.env;
    if (!env?.AI) return Response.json({ error: 'Workers AI no vinculado (binding [ai] en wrangler.toml)' }, { status: 503 });
    const limpios = messages
      .filter(m => ['system', 'user', 'assistant'].includes(m.role) && String(m.content).length < 4000)
      .slice(-20);
    const r: any = await env.AI.run('@cf/meta/llama-3.1-8b-instruct', {
      messages: limpios, max_tokens: 900, temperature: 0.35,
    });
    return Response.json({ respuesta: r?.response || '' });
  } catch (e: any) {
    return Response.json({ error: 'Tutor ocupado: ' + (e?.message || e) }, { status: 500 });
  }
};
