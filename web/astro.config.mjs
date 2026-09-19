import { defineConfig } from 'astro/config';
import cloudflare from '@astrojs/cloudflare';

// Modo híbrido: páginas estáticas (GitHub Pages gratis) + APIs serverless (Cloudflare Workers, tier gratis).
// Base por defecto = GitHub Pages. Para el deploy en Cloudflare (backend en raíz):
//   ASTRO_BASE=/ npm run build
export default defineConfig({
  site: 'https://softengai-dev.github.io',
  base: process.env.ASTRO_BASE || '/plataforma-total-pro/app',
  output: 'hybrid',
  adapter: cloudflare({ platformProxy: { enabled: true } }),
});
