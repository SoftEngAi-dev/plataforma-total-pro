globalThis.process ??= {}; globalThis.process.env ??= {};
export { renderers } from '../../renderers.mjs';

const prerender = false;
const GET = async ({ locals }) => {
  const env = locals.runtime?.env;
  const db = !!env?.DB;
  const ai = !!env?.AI;
  return Response.json({
    ok: true,
    service: "plataforma-total-api",
    version: "5.0.0",
    mode: db ? ai ? "cloud+ai" : "cloud" : "degraded",
    capabilities: {
      auth: db,
      progress: db,
      certificates: db,
      pro: db,
      chat_ai: ai,
      course_api: true
    }
  });
};

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  GET,
  prerender
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
