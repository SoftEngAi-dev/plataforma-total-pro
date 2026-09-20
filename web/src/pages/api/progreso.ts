// 💾 GET/POST /api/progreso — sincroniza el estado de aprendizaje por sesión
import type { APIRoute } from 'astro';

export const prerender = false;

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type, X-Token',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
};
export const OPTIONS: APIRoute = () => new Response(null, { status: 204, headers: CORS });
const J = (d: unknown, status = 200) => Response.json(d, { status, headers: CORS });

async function aliasDe(request: Request, env: any): Promise<string | null> {
  const t = request.headers.get('X-Token') || '';
  if (t.length < 16) return null;
  const s = await env.DB.prepare('SELECT alias, expira FROM sessions WHERE token = ?').bind(t).first();
  if (!s || new Date(s.expira as string) < new Date()) return null;
  return s.alias as string;
}

export const GET: APIRoute = async ({ request, locals }) => {
  try {
    const env = (locals as any).runtime?.env;
    if (!env?.DB) return J({ ok: false, error: 'sin DB' }, 503);
    const a = await aliasDe(request, env);
    if (!a) return J({ ok: false, error: 'sesión inválida' }, 401);
    const r = await env.DB.prepare('SELECT data FROM progreso WHERE alias = ?').bind(a).first();
    return J({ ok: true, data: r ? JSON.parse(r.data as string) : null });
  } catch (e: any) {
    return J({ ok: false, error: String(e?.message || e) }, 500);
  }
};

export const POST: APIRoute = async ({ request, locals }) => {
  try {
    const env = (locals as any).runtime?.env;
    if (!env?.DB) return J({ ok: false, error: 'sin DB' }, 503);
    const a = await aliasDe(request, env);
    if (!a) return J({ ok: false, error: 'sesión inválida' }, 401);
    const { data } = await request.json() as { data: unknown };
    const txt = JSON.stringify(data ?? {});
    if (txt.length > 200_000) return J({ ok: false, error: 'demasiado grande' }, 413);
    await env.DB.prepare(
      'INSERT INTO progreso (alias, data, actualizado) VALUES (?, ?, ?) ' +
      'ON CONFLICT(alias) DO UPDATE SET data = excluded.data, actualizado = excluded.actualizado'
    ).bind(a, txt, new Date().toISOString()).run();
    return J({ ok: true });
  } catch (e: any) {
    return J({ ok: false, error: String(e?.message || e) }, 500);
  }
};
