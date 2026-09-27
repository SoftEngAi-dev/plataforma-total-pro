globalThis.process ??= {}; globalThis.process.env ??= {};
export { renderers } from '../../renderers.mjs';

const prerender = false;
const J = (d, status = 200) => Response.json(d, {
  status,
  headers: {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type, X-Token",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Cache-Control": "public, max-age=300"
  }
});
const OPTIONS = () => new Response(null, {
  status: 204,
  headers: {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type, X-Token",
    "Access-Control-Allow-Methods": "GET, OPTIONS"
  }
});
const GET = async ({ request }) => {
  const slug = new URL(request.url).searchParams.get("slug") || "";
  if (!/^[a-z0-9-]{3,80}$/i.test(slug)) return J({ ok: false, error: "slug inválido" }, 400);
  const target = new URL("/data/cursos/" + slug + ".json", request.url);
  const r = await fetch(target);
  if (!r.ok) return J({ ok: false, error: "curso no encontrado" }, 404);
  const data = await r.json();
  return J({ ok: true, data });
};

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  GET,
  OPTIONS,
  prerender
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
