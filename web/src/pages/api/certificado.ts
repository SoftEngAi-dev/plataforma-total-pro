// 📜 /api/certificado — registro y verificación pública de certificados
// POST (X-Token) {codigo, curso} → registra el código generado en el cliente
// GET  ?codigo=PT-XXXX          → verificación pública (sin sesión, alias enmascarado)
import type { APIRoute } from 'astro';

export const prerender = false;

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type, X-Token',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
};
export const OPTIONS: APIRoute = () => new Response(null, { status: 204, headers: CORS });
const J = (d: unknown, status = 200) => Response.json(d, { status, headers: CORS });

const enmascarar = (a: string) => a.length <= 3 ? a[0] + '***' : a.slice(0, 3) + '***';

export const POST: APIRoute = async ({ request, locals }) => {
  try {
    const env = (locals as any).runtime?.env;
    if (!env?.DB) return J({ ok: false, error: 'sin DB' }, 503);
    const t = request.headers.get('X-Token') || '';
    if (t.length < 16) return J({ ok: false, error: 'sesión inválida' }, 401);
    const s = await env.DB.prepare('SELECT alias, expira FROM sessions WHERE token = ?').bind(t).first();
    if (!s || new Date(s.expira as string) < new Date()) return J({ ok: false, error: 'sesión inválida' }, 401);

    const { codigo, curso } = await request.json() as { codigo: string; curso: string };
    const cod = String(codigo || '').trim().toUpperCase().slice(0, 20);
    const cur = String(curso || '').trim().slice(0, 80);
    if (!/^PT-[A-Z0-9-]{3,15}$/.test(cod)) return J({ ok: false, error: 'código inválido' });
    if (!cur) return J({ ok: false, error: 'curso requerido' });

    await env.DB.prepare('INSERT OR IGNORE INTO certificados (codigo, alias, curso, fecha) VALUES (?, ?, ?, ?)')
      .bind(cod, s.alias, cur, new Date().toISOString().slice(0, 10)).run();
    return J({ ok: true, codigo: cod });
  } catch (e: any) {
    return J({ ok: false, error: String(e?.message || e) }, 500);
  }
};

export const GET: APIRoute = async ({ url, locals }) => {
  try {
    const env = (locals as any).runtime?.env;
    if (!env?.DB) return J({ ok: false, error: 'sin DB' }, 503);
    let cod = String(url.searchParams.get('codigo') || '').trim().toUpperCase();
    if (!cod) return J({ ok: false, error: 'falta ?codigo=' }, 400);
    let r = await env.DB.prepare('SELECT alias, curso, fecha FROM certificados WHERE codigo = ?').bind(cod).first();
    if (!r && !cod.startsWith('PT-')) {  // la app de escritorio muestra el código sin prefijo
      r = await env.DB.prepare('SELECT alias, curso, fecha FROM certificados WHERE codigo = ?').bind('PT-' + cod).first();
    }
    if (!r) return J({ ok: true, valido: false });
    return J({ ok: true, valido: true, quien: enmascarar(String(r.alias)), curso: r.curso, fecha: r.fecha });
  } catch (e: any) {
    return J({ ok: false, error: String(e?.message || e) }, 500);
  }
};
