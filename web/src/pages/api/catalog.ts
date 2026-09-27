import type { APIRoute } from 'astro';
import indiceRaw from '../../../public/data/indice.json?raw';

export const prerender = false;

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type, X-Token',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
};
export const OPTIONS: APIRoute = () => new Response(null, { status: 204, headers: CORS });

export const GET: APIRoute = async () => {
  const data = JSON.parse(indiceRaw);
  return Response.json({
    ok: true,
    version: '5.1.0',
    stats: {
      courses: data.length,
      free_courses: data.filter((c: any) => c.free).length,
      lessons: data.reduce((n: number, c: any) => n + Number(c.l || 0), 0),
      quizzes: data.length ? 658 : 0,
    },
    data,
  }, { headers: { ...CORS, 'Cache-Control': 'public, max-age=300' } });
};
