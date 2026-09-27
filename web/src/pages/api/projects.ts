import type { APIRoute } from 'astro';

export const prerender = false;

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type, X-Token',
  'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
};
export const OPTIONS: APIRoute = () => new Response(null, { status: 204, headers: CORS });
const J = (d: unknown, status = 200) => Response.json(d, { status, headers: CORS });

async function aliasDe(request: Request, env: any): Promise<string | null> {
  const token = request.headers.get('X-Token') || '';
  if (token.length < 16) return null;
  const row = await env.DB.prepare('SELECT alias, expira FROM sessions WHERE token = ?').bind(token).first();
  if (!row || new Date(String(row.expira)) < new Date()) return null;
  return String(row.alias);
}

export const GET: APIRoute = async ({ request, locals }) => {
  const env = (locals as any).runtime?.env;
  if (!env?.DB) return J({ ok: false, error: 'D1 sin configurar' }, 503);
  const alias = await aliasDe(request, env);
  if (!alias) return J({ ok: false, error: 'sesión inválida' }, 401);
  const rows = await env.DB.prepare(
    'SELECT id,name,metadata,created,updated FROM projects WHERE alias=? ORDER BY updated DESC'
  ).bind(alias).all();
  return J({
    ok: true,
    projects: (rows.results || []).map((r: any) => ({
      id: r.id, name: r.name, metadata: r.metadata ? JSON.parse(r.metadata) : {},
      created: r.created, updated: r.updated,
    })),
  });
};

export const POST: APIRoute = async ({ request, locals }) => {
  const env = (locals as any).runtime?.env;
  if (!env?.DB) return J({ ok: false, error: 'D1 sin configurar' }, 503);
  const alias = await aliasDe(request, env);
  if (!alias) return J({ ok: false, error: 'sesión inválida' }, 401);
  const body = await request.json() as any;
  const name = String(body?.name || '').trim().slice(0, 100) || 'Proyecto sin nombre';
  const metadata = JSON.stringify({
    language: String(body?.language || '').slice(0, 40),
    template: String(body?.template || 'base').slice(0, 40),
  });
  const id = crypto.randomUUID();
  const stamp = new Date().toISOString();
  await env.DB.prepare(
    'INSERT INTO projects(id,alias,name,metadata,created,updated) VALUES(?,?,?,?,?,?)'
  ).bind(id, alias, name, metadata, stamp, stamp).run();
  return J({ ok: true, project: { id, name, metadata: JSON.parse(metadata), created: stamp, updated: stamp } }, 201);
};

export const DELETE: APIRoute = async ({ request, locals }) => {
  const env = (locals as any).runtime?.env;
  if (!env?.DB) return J({ ok: false, error: 'D1 sin configurar' }, 503);
  const alias = await aliasDe(request, env);
  if (!alias) return J({ ok: false, error: 'sesión inválida' }, 401);
  const id = new URL(request.url).searchParams.get('id') || '';
  const result = await env.DB.prepare('DELETE FROM projects WHERE id=? AND alias=?').bind(id, alias).run();
  return result.meta?.changes ? J({ ok: true }) : J({ ok: false, error: 'proyecto no encontrado' }, 404);
};
