import type { APIRoute } from 'astro';
import indiceRaw from '../../../public/data/indice.json?raw';

export const prerender = false;

export const GET: APIRoute = async () => {
  const data = JSON.parse(indiceRaw);
  return Response.json({
    ok: true,
    version: '5.0.0',
    stats: {
      courses: data.length,
      free_courses: data.filter((c: any) => c.free).length,
      lessons: data.reduce((n: number, c: any) => n + Number(c.l || 0), 0),
    },
    data,
  }, { headers: { 'Cache-Control': 'public, max-age=300' } });
};
