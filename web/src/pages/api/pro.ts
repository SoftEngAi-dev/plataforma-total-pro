// 💎 /api/pro — estado PRO de la sesión y activación por email de compra
// GET  (X-Token)          → { ok, pro }        consulta si el alias está vinculado a un email PRO activo
// POST (X-Token) {email}  → { ok, pro }        vincula alias↔email si ese email compró (fallback al passthrough)
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

async function esPro(env: any, alias: string): Promise<boolean> {
  const v = await env.DB.prepare(
    'SELECT p.estado FROM pro_alias pa JOIN pro p ON p.email = pa.email WHERE pa.alias = ?'
  ).bind(alias).first();
  return !!v && v.estado === 1;
}

export const GET: APIRoute = async ({ request, locals }) => {
  try {
    const env = (locals as any).runtime?.env;
    if (!env?.DB) return J({ ok: false, error: 'sin DB' }, 503);
    const a = await aliasDe(request, env);
    if (!a) return J({ ok: false, error: 'sesión inválida' }, 401);
    return J({ ok: true, pro: await esPro(env, a) });
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
    if (await esPro(env, a)) return J({ ok: true, pro: true });

    const { email } = await request.json() as { email: string };
    const em = String(email || '').trim().toLowerCase();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em)) return J({ ok: false, error: 'email inválido' });

    const fila = await env.DB.prepare('SELECT estado FROM pro WHERE email = ?').bind(em).first();
    if (!fila || fila.estado !== 1) {
      return J({ ok: false, pro: false, error: 'Ese email no tiene una compra PRO activa. Revisá que sea el email exacto del recibo de Lemon Squeezy.' }, 404);
    }
    await env.DB.prepare(
      'INSERT INTO pro_alias (alias, email, actualizado) VALUES (?, ?, ?) ' +
      'ON CONFLICT(alias) DO UPDATE SET email = excluded.email, actualizado = excluded.actualizado'
    ).bind(a, em, new Date().toISOString()).run();
    return J({ ok: true, pro: true });
  } catch (e: any) {
    return J({ ok: false, error: String(e?.message || e) }, 500);
  }
};
