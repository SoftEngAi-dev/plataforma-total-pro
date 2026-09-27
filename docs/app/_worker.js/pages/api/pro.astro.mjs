globalThis.process ??= {}; globalThis.process.env ??= {};
export { renderers } from '../../renderers.mjs';

const prerender = false;
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "Content-Type, X-Token",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
};
const OPTIONS = () => new Response(null, { status: 204, headers: CORS });
const J = (d, status = 200) => Response.json(d, { status, headers: CORS });
async function aliasDe(request, env) {
  const t = request.headers.get("X-Token") || "";
  if (t.length < 16) return null;
  const s = await env.DB.prepare("SELECT alias, expira FROM sessions WHERE token = ?").bind(t).first();
  if (!s || new Date(s.expira) < /* @__PURE__ */ new Date()) return null;
  return s.alias;
}
async function esPro(env, alias) {
  const v = await env.DB.prepare(
    "SELECT p.estado FROM pro_alias pa JOIN pro p ON p.email = pa.email WHERE pa.alias = ?"
  ).bind(alias).first();
  return !!v && v.estado === 1;
}
const GET = async ({ request, locals }) => {
  try {
    const env = locals.runtime?.env;
    if (!env?.DB) return J({ ok: false, error: "sin DB" }, 503);
    const a = await aliasDe(request, env);
    if (!a) return J({ ok: false, error: "sesión inválida" }, 401);
    return J({ ok: true, pro: await esPro(env, a) });
  } catch (e) {
    return J({ ok: false, error: String(e?.message || e) }, 500);
  }
};
const POST = async ({ request, locals }) => {
  try {
    const env = locals.runtime?.env;
    if (!env?.DB) return J({ ok: false, error: "sin DB" }, 503);
    const a = await aliasDe(request, env);
    if (!a) return J({ ok: false, error: "sesión inválida" }, 401);
    if (await esPro(env, a)) return J({ ok: true, pro: true });
    const { email } = await request.json();
    const em = String(email || "").trim().toLowerCase();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em)) return J({ ok: false, error: "email inválido" });
    const fila = await env.DB.prepare("SELECT estado FROM pro WHERE email = ?").bind(em).first();
    if (!fila || fila.estado !== 1) {
      return J({ ok: false, pro: false, error: "Ese email no tiene una compra PRO activa. Revisá que sea el email exacto del recibo de Lemon Squeezy." }, 404);
    }
    await env.DB.prepare(
      "INSERT INTO pro_alias (alias, email, actualizado) VALUES (?, ?, ?) ON CONFLICT(alias) DO UPDATE SET email = excluded.email, actualizado = excluded.actualizado"
    ).bind(a, em, (/* @__PURE__ */ new Date()).toISOString()).run();
    return J({ ok: true, pro: true });
  } catch (e) {
    return J({ ok: false, error: String(e?.message || e) }, 500);
  }
};

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  GET,
  OPTIONS,
  POST,
  prerender
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
