globalThis.process ??= {}; globalThis.process.env ??= {};
export { renderers } from '../../renderers.mjs';

const prerender = false;
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "Content-Type, X-Token",
  "Access-Control-Allow-Methods": "POST, OPTIONS"
};
const OPTIONS = () => new Response(null, { status: 204, headers: CORS });
const J = (d, status = 200) => Response.json(d, { status, headers: CORS });
const eq = (a, b) => {
  if (a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
};
const POST = async ({ request, locals }) => {
  try {
    const env = locals.runtime?.env;
    if (!env?.DB) return J({ ok: false, error: "sin DB" }, 503);
    if (!env?.ADMIN_SECRET) return J({ ok: false, error: "ADMIN_SECRET no configurado (wrangler pages secret put)" }, 503);
    const { secret, email, accion, nota } = await request.json();
    if (!eq(String(secret || ""), env.ADMIN_SECRET)) return J({ ok: false, error: "no autorizado" }, 401);
    const em = String(email || "").trim().toLowerCase();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em)) return J({ ok: false, error: "email inválido" });
    const quitar = String(accion || "pro") === "quitar";
    const estado = quitar ? 0 : 1;
    await env.DB.prepare(
      "INSERT INTO pro (email, estado, order_id, evento, actualizado) VALUES (?, ?, ?, ?, ?) ON CONFLICT(email) DO UPDATE SET estado = excluded.estado, order_id = excluded.order_id, evento = excluded.evento, actualizado = excluded.actualizado"
    ).bind(em, estado, "manual:" + String(nota || "").slice(0, 60), quitar ? "admin_quitar" : "admin_pro", (/* @__PURE__ */ new Date()).toISOString()).run();
    return J({ ok: true, email: em, estado, msg: estado ? "💎 PRO otorgado — el usuario activa con este email en /pro/ o en su próxima sync" : "PRO revocado" });
  } catch (e) {
    return J({ ok: false, error: String(e?.message || e) }, 500);
  }
};

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  OPTIONS,
  POST,
  prerender
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
