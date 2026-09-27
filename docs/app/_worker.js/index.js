globalThis.process ??= {}; globalThis.process.env ??= {};
import { renderers } from './renderers.mjs';
import { createExports } from './_@astrojs-ssr-adapter.mjs';
import { manifest } from './manifest_DqdB9fDL.mjs';

const _page0 = () => import('./pages/_image.astro.mjs');
const _page1 = () => import('./pages/api/admin.astro.mjs');
const _page2 = () => import('./pages/api/auth.astro.mjs');
const _page3 = () => import('./pages/api/catalog.astro.mjs');
const _page4 = () => import('./pages/api/certificado.astro.mjs');
const _page5 = () => import('./pages/api/chat.astro.mjs');
const _page6 = () => import('./pages/api/course.astro.mjs');
const _page7 = () => import('./pages/api/health.astro.mjs');
const _page8 = () => import('./pages/api/pago.astro.mjs');
const _page9 = () => import('./pages/api/pro.astro.mjs');
const _page10 = () => import('./pages/api/progreso.astro.mjs');
const _page11 = () => import('./pages/api/projects.astro.mjs');
const _page12 = () => import('./pages/aprender.astro.mjs');
const _page13 = () => import('./pages/certificados.astro.mjs');
const _page14 = () => import('./pages/chat.astro.mjs');
const _page15 = () => import('./pages/evaluacion.astro.mjs');
const _page16 = () => import('./pages/ingles.astro.mjs');
const _page17 = () => import('./pages/lab.astro.mjs');
const _page18 = () => import('./pages/pomo.astro.mjs');
const _page19 = () => import('./pages/pro.astro.mjs');
const _page20 = () => import('./pages/progreso.astro.mjs');
const _page21 = () => import('./pages/proyectos.astro.mjs');
const _page22 = () => import('./pages/rutas.astro.mjs');
const _page23 = () => import('./pages/verificar.astro.mjs');
const _page24 = () => import('./pages/index.astro.mjs');

const pageMap = new Map([
    ["node_modules/@astrojs/cloudflare/dist/entrypoints/image-endpoint.js", _page0],
    ["src/pages/api/admin.ts", _page1],
    ["src/pages/api/auth.ts", _page2],
    ["src/pages/api/catalog.ts", _page3],
    ["src/pages/api/certificado.ts", _page4],
    ["src/pages/api/chat.ts", _page5],
    ["src/pages/api/course.ts", _page6],
    ["src/pages/api/health.ts", _page7],
    ["src/pages/api/pago.ts", _page8],
    ["src/pages/api/pro.ts", _page9],
    ["src/pages/api/progreso.ts", _page10],
    ["src/pages/api/projects.ts", _page11],
    ["src/pages/aprender.astro", _page12],
    ["src/pages/certificados.astro", _page13],
    ["src/pages/chat.astro", _page14],
    ["src/pages/evaluacion.astro", _page15],
    ["src/pages/ingles.astro", _page16],
    ["src/pages/lab.astro", _page17],
    ["src/pages/pomo.astro", _page18],
    ["src/pages/pro.astro", _page19],
    ["src/pages/progreso.astro", _page20],
    ["src/pages/proyectos.astro", _page21],
    ["src/pages/rutas.astro", _page22],
    ["src/pages/verificar.astro", _page23],
    ["src/pages/index.astro", _page24]
]);
const serverIslandMap = new Map();
const _manifest = Object.assign(manifest, {
    pageMap,
    serverIslandMap,
    renderers,
    middleware: () => import('./_astro-internal_middleware.mjs')
});
const _exports = createExports(_manifest);
const __astrojsSsrVirtualEntry = _exports.default;

export { __astrojsSsrVirtualEntry as default, pageMap };
