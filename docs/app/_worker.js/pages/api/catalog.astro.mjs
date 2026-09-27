globalThis.process ??= {}; globalThis.process.env ??= {};
import { i as indiceRaw } from '../../chunks/indice_B2IefIdn.mjs';
export { renderers } from '../../renderers.mjs';

const prerender = false;
const GET = async () => {
  const data = JSON.parse(indiceRaw);
  return Response.json({
    ok: true,
    version: "5.0.0",
    stats: {
      courses: data.length,
      free_courses: data.filter((c) => c.free).length,
      lessons: data.reduce((n, c) => n + Number(c.l || 0), 0)
    },
    data
  }, { headers: { "Cache-Control": "public, max-age=300" } });
};

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  GET,
  prerender
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
