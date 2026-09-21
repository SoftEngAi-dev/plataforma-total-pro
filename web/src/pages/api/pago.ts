// 💎 POST /api/pago — Webhook de Lemon Squeezy (activa/desactiva PRO)
// Firma: X-Signature = HMAC-SHA256(raw body, secret) en hex. Secret = env LS_SECRET.
// Formato JSON:API: meta.event_name, meta.custom_data (passthrough del checkout), data.attributes.
import type { APIRoute } from 'astro';

export const prerender = false;

async function hmacHex(secret: string, body: string): Promise<string> {
  const enc = new TextEncoder();
  const k = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const sig = await crypto.subtle.sign('HMAC', k, enc.encode(body));
  return Array.from(new Uint8Array(sig)).map(b => b.toString(16).padStart(2, '0')).join('');
}
// comparación en tiempo constante (anti timing attacks)
const hexEq = (a: string, b: string) => {
  if (a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
};

// eventos → estado PRO (LS 2026)
const ACTIVA = new Set(['order_created', 'subscription_created', 'subscription_resumed',
  'subscription_unpaused', 'subscription_payment_success', 'subscription_payment_recovered']);
const DESACTIVA = new Set(['order_refunded', 'subscription_cancelled', 'subscription_expired',
  'subscription_payment_failed']);

export const POST: APIRoute = async ({ request, locals }) => {
  try {
    const env = (locals as any).runtime?.env;
    if (!env?.DB) return Response.json({ error: 'sin DB' }, { status: 503 });
    if (!env?.LS_SECRET) return Response.json({ error: 'LS_SECRET no configurado (wrangler pages secret put LS_SECRET)' }, { status: 503 });

    const body = await request.text();
    const sig = request.headers.get('x-signature') || '';
    const esperada = await hmacHex(env.LS_SECRET, body);
    if (!hexEq(sig.toLowerCase(), esperada)) return Response.json({ error: 'firma inválida' }, { status: 401 });

    const p = JSON.parse(body);
    const evento: string = p?.meta?.event_name || '';
    const attrs = p?.data?.attributes || {};
    const email = String(attrs.user_email || '').trim().toLowerCase();
    const aliasCustom = String(p?.meta?.custom_data?.alias || '').trim().toLowerCase();

    let estado: number | null = null;
    if (ACTIVA.has(evento) && (attrs.status === 'paid' || attrs.status === 'active' || evento !== 'order_created')) estado = 1;
    if (DESACTIVA.has(evento)) estado = 0;
    if (estado === null) return Response.json({ ok: true, ignorado: evento }); // eventos no relevantes (license, etc.)

    if (!email) return Response.json({ error: 'payload sin user_email' }, { status: 400 });

    const ahora = new Date().toISOString();
    await env.DB.prepare(
      'INSERT INTO pro (email, estado, order_id, evento, actualizado) VALUES (?, ?, ?, ?, ?) ' +
      'ON CONFLICT(email) DO UPDATE SET estado = excluded.estado, order_id = excluded.order_id, evento = excluded.evento, actualizado = excluded.actualizado'
    ).bind(email, estado, String(p?.data?.id || ''), evento, ahora).run();

    // si el checkout trajo alias (custom passthrough), vincular automáticamente
    if (aliasCustom && /^[a-z0-9_]{3,24}$/.test(aliasCustom)) {
      await env.DB.prepare(
        'INSERT INTO pro_alias (alias, email, actualizado) VALUES (?, ?, ?) ' +
        'ON CONFLICT(alias) DO UPDATE SET email = excluded.email, actualizado = excluded.actualizado'
      ).bind(aliasCustom, email, ahora).run();
    }
    return Response.json({ ok: true, evento, estado });
  } catch (e: any) {
    return Response.json({ error: 'webhook: ' + (e?.message || e) }, { status: 500 });
  }
};
