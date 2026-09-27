import type { APIRoute } from 'astro';

export const prerender = false;

export const GET: APIRoute = async ({ locals }) => {
  const env = (locals as any).runtime?.env;
  const db = !!env?.DB;
  const ai = !!env?.AI;
  return Response.json({
    ok: true,
    service: 'plataforma-total-api',
    version: '5.0.0',
    mode: db ? (ai ? 'cloud+ai' : 'cloud') : 'degraded',
    capabilities: {
      auth: db,
      progress: db,
      certificates: db,
      pro: db,
      chat_ai: ai,
      course_api: true,
    },
  });
};
