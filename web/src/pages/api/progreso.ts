// 💾 GET/POST /api/progreso — sincroniza el estado de aprendizaje por sesión
import type { APIRoute } from 'astro';

export const prerender = false;

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
    if (!env?.DB) return Response.json({ ok: false, error: 'sin DB' }, { status: 503 });
    const a = await aliasDe(request, env);
    if (!a) return Response.json({ ok: false, error: 'sesión inválida' }, { status: 401 });
    const r = await env.DB.prepare('SELECT data FROM progreso WHERE alias = ?').bind(a).first();
    return Response.json({ ok: true, data: r ? JSON.parse(r.data as string) : null });
  } catch (e: any) {
    return Response.json({ ok: false, error: String(e?.message || e) }, { status: 500 });
  }
};

export const POST: APIRoute = async ({ request, locals }) => {
  try {
    const env = (locals as any).runtime?.env;
    if (!env?.DB) return Response.json({ ok: false, error: 'sin DB' }, { status: 503 });
    const a = await aliasDe(request, env);
    if (!a) return Response.json({ ok: false, error: 'sesión inválida' }, { status: 401 });
    const { data } = await request.json() as { data: unknown };
    const txt = JSON.stringify(data ?? {});
    if (txt.length > 200_000) return Response.json({ ok: false, error: 'demasiado grande' }, { status: 413 });
    await env.DB.prepare(
      'INSERT INTO progreso (alias, data, actualizado) VALUES (?, ?, ?) ' +
      'ON CONFLICT(alias) DO UPDATE SET data = excluded.data, actualizado = excluded.actualizado'
    ).bind(a, txt, new Date().toISOString()).run();
    return Response.json({ ok: true });
  } catch (e: any) {
    return Response.json({ ok: false, error: String(e?.message || e) }, { status: 500 });
  }
};
