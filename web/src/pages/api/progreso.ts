// 💾 GET/POST /api/progreso — estado de aprendizaje persistente y merge por entidad
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

function mergeQuiz(a: any, b: any) {
  const out = { ...(a || {}) };
  for (const [k, v0] of Object.entries(b || {})) {
    const v: any = v0 || {};
    const old: any = out[k];
    if (!old) { out[k] = v; continue; }
    out[k] = {
      correct: Math.max(Number(old.correct || 0), Number(v.correct || 0)),
      answered: Math.max(Number(old.answered || 0), Number(v.answered || 0)),
      total: Math.max(Number(old.total || 0), Number(v.total || 0)),
      updated_at: [old.updated_at, v.updated_at].filter(Boolean).sort().pop() || null,
    };
  }
  return out;
}

function mergeState(a: any, b: any) {
  const leidas: Record<string, number[]> = { ...(a.leidas || {}) };
  for (const [curso, arr0] of Object.entries(b.leidas || {})) {
    const arr = Array.isArray(arr0) ? arr0.map(Number).filter(Number.isInteger) : [];
    leidas[curso] = Array.from(new Set([...(leidas[curso] || []), ...arr])).sort((x, y) => x - y);
  }
  const dias = Array.from(new Set([...(a.dias_activos || []), ...(b.dias_activos || [])])).sort();
  const completados = Array.from(new Set([...(a.completados || []), ...(b.completados || [])]));
  const quiz_lessons = mergeQuiz(a.quiz_lessons, b.quiz_lessons);
  const ultima = [a.ultima, b.ultima].filter(Boolean).sort((x: any, y: any) => Number(y.at || 0) - Number(x.at || 0))[0] || null;
  const quiz_tot = Object.keys(quiz_lessons).length;
  const quiz_ok = Object.values(quiz_lessons).filter((x: any) => Number(x.correct || 0) >= Number(x.total || 0) && Number(x.total || 0) > 0).length;
  return {
    ...a,
    ...b,
    leidas,
    dias_activos: dias,
    completados,
    quiz_lessons,
    quiz_tot,
    quiz_ok,
    xp: Math.max(Number(a.xp || 0), Number(b.xp || 0)),
    racha: {
      n: Math.max(Number(a.racha?.n || 0), Number(b.racha?.n || 0)),
      ultimo: a.racha?.ultimo || b.racha?.ultimo || null,
    },
    ultima,
    updated_at: new Date().toISOString(),
  };
}

export const GET: APIRoute = async ({ request, locals }) => {
  try {
    const env = (locals as any).runtime?.env;
    if (!env?.DB) return J({ ok: false, error: 'D1 sin configurar' }, 503);
    const alias = await aliasDe(request, env);
    if (!alias) return J({ ok: false, error: 'sesión inválida' }, 401);
    const r = await env.DB.prepare('SELECT data FROM progreso WHERE alias = ?').bind(alias).first();
    return J({ ok: true, data: r?.data ? JSON.parse(String(r.data)) : null });
  } catch (e: any) {
    return J({ ok: false, error: String(e?.message || e) }, 500);
  }
};

export const POST: APIRoute = async ({ request, locals }) => {
  try {
    const env = (locals as any).runtime?.env;
    if (!env?.DB) return J({ ok: false, error: 'D1 sin configurar' }, 503);
    const alias = await aliasDe(request, env);
    if (!alias) return J({ ok: false, error: 'sesión inválida' }, 401);
    const body = await request.json() as { data?: unknown };
    const incoming = body?.data && typeof body.data === 'object' ? body.data as any : {};
    if (JSON.stringify(incoming).length > 250_000) return J({ ok: false, error: 'progreso demasiado grande' }, 413);
    const row = await env.DB.prepare('SELECT data FROM progreso WHERE alias = ?').bind(alias).first();
    let current: any = {};
    try { current = row?.data ? JSON.parse(String(row.data)) : {}; } catch {}
    const merged = mergeState(current, incoming);
    await env.DB.prepare(
      'INSERT INTO progreso (alias, data, actualizado) VALUES (?, ?, ?) ' +
      'ON CONFLICT(alias) DO UPDATE SET data = excluded.data, actualizado = excluded.actualizado'
    ).bind(alias, JSON.stringify(merged), merged.updated_at).run();
    return J({ ok: true, data: merged });
  } catch (e: any) {
    return J({ ok: false, error: String(e?.message || e) }, 500);
  }
};
