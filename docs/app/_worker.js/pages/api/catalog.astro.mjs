globalThis.process ??= {}; globalThis.process.env ??= {};
import { i as indiceRaw } from '../../chunks/indice_D54Cn72X.mjs';
export { renderers } from '../../renderers.mjs';

const prerender = false;
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "Content-Type, X-Token",
  "Access-Control-Allow-Methods": "GET, OPTIONS"
};
const OPTIONS = () => new Response(null, { status: 204, headers: CORS });
const GET = async () => {
  const data = JSON.parse(indiceRaw);
  return Response.json({
    ok: true,
    version: "5.1.0",
    stats: {
      courses: data.length,
      free_courses: data.filter((c) => c.free).length,
      lessons: data.reduce((n, c) => n + Number(c.l || 0), 0),
      quizzes: data.length ? 658 : 0
    },
    data
  }, { headers: { ...CORS, "Cache-Control": "public, max-age=300" } });
};

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  GET,
  OPTIONS,
  prerender
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
