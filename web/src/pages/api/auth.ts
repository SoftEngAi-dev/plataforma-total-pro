// 🔑 POST /api/auth — login/registro alias + PIN (PBKDF2-SHA256, WebCrypto nativo del edge)
import type { APIRoute } from 'astro';

export const prerender = false;

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type, X-Token',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
};
export const OPTIONS: APIRoute = () => new Response(null, { status: 204, headers: CORS });
const J = (d: unknown, status = 200) => Response.json(d, { status, headers: CORS });

async function pbkdf2(pin: string, saltHex: string): Promise<string> {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey('raw', enc.encode(pin), 'PBKDF2', false, ['deriveBits']);
  const salt = Uint8Array.from(saltHex.match(/.{2}/g)!.map(h => parseInt(h, 16)));
  const bits = await crypto.subtle.deriveBits({ name: 'PBKDF2', hash: 'SHA-256', salt, iterations: 100_000 }, key, 256);
  return Array.from(new Uint8Array(bits)).map(b => b.toString(16).padStart(2, '0')).join('');
}
const randHex = (n: number) =>
  Array.from(crypto.getRandomValues(new Uint8Array(n))).map(b => b.toString(16).padStart(2, '0')).join('');

export const POST: APIRoute = async ({ request, locals }) => {
  try {
    const { alias, pin } = await request.json() as { alias: string; pin: string };
    const env = (locals as any).runtime?.env;
    if (!env?.DB) return J({ ok: false, error: 'D1 no vinculado ([[d1_databases]] en wrangler.toml)' }, 503);
    const a = String(alias || '').trim().toLowerCase().slice(0, 24);
    if (!/^[a-z0-9_]{3,24}$/.test(a)) return J({ ok: false, error: 'Alias inválido (3-24: letras/números/_)' });
    if (!pin || String(pin).length < 4) return J({ ok: false, error: 'PIN de 4+ caracteres' });

    const u = await env.DB.prepare('SELECT hash, salt FROM users WHERE alias = ?').bind(a).first();
    // 🛡️ anti fuerza bruta: 5 PIN erróneos en 10 min → bloqueo temporal
    const ahora = Date.now();
    const int = await env.DB.prepare('SELECT n, ts FROM intentos WHERE alias = ?').bind(a).first();
    const fallos = (int && ahora - Date.parse(String(int.ts)) < 600_000) ? Number(int.n) : 0;
    if (fallos >= 5) {
      return J({ ok: false, error: 'Demasiados intentos fallidos. Esperá ~10 minutos.' }, 429);
    }
    if (u) {
      const h = await pbkdf2(String(pin), u.salt as string);
      if (h !== u.hash) {
        const iso = new Date(ahora).toISOString();
        await env.DB.prepare(
          'INSERT INTO intentos (alias, n, ts) VALUES (?, 1, ?) ' +
          'ON CONFLICT(alias) DO UPDATE SET n = ?, ts = ?'
        ).bind(a, iso, fallos + 1, iso).run();
        return J({ ok: false, error: 'PIN incorrecto para ese alias' }, 401);
      }
      await env.DB.prepare('DELETE FROM intentos WHERE alias = ?').bind(a).run();
    } else {
      const salt = randHex(16);
      const h = await pbkdf2(String(pin), salt);
      await env.DB.prepare('INSERT INTO users (alias, hash, salt, creado) VALUES (?, ?, ?, ?)')
        .bind(a, h, salt, new Date().toISOString()).run();
    }
    const token = randHex(24);
    const expira = new Date(Date.now() + 30 * 864e5).toISOString();
    await env.DB.prepare('INSERT INTO sessions (token, alias, expira) VALUES (?, ?, ?)').bind(token, a, expira).run();
    return J({ ok: true, alias: a, token });
  } catch (e: any) {
    return J({ ok: false, error: 'Error de auth: ' + (e?.message || e) }, 500);
  }
};
