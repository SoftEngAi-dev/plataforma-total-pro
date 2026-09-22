#!/usr/bin/env python3
"""🗺️ Genera web/public/robots.txt + sitemap.xml (SEO/GEO).
Re-ejecutar si cambian rutas o cantidad de cursos."""
import json, os, datetime

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(RAIZ, 'web', 'public')
DOMINIO = 'https://plataforma-total-web.pages.dev'
HOY = datetime.date.today().isoformat()

RUTAS = [
    ('/', '1.0', 'weekly'),
    ('/aprender/', '0.9', 'weekly'),
    ('/rutas/', '0.8', 'monthly'),
    ('/pro/', '0.8', 'monthly'),
    ('/progreso/', '0.5', 'monthly'),
    ('/evaluacion/', '0.5', 'monthly'),
    ('/certificados/', '0.5', 'monthly'),
    ('/lab/', '0.6', 'monthly'),
    ('/chat/', '0.6', 'monthly'),
    ('/pomo/', '0.4', 'monthly'),
    ('/ingles/', '0.6', 'monthly'),
]
n_cursos = len(json.load(open(os.path.join(PUB, 'data', 'indice.json'))))
RUTAS += [(f'/curso/{i}', '0.7', 'monthly') for i in range(1, n_cursos + 1)]

urls = ''.join(
    f"  <url><loc>{DOMINIO}{r}</loc><lastmod>{HOY}</lastmod><changefreq>{f}</changefreq><priority>{p}</priority></url>\n"
    for r, p, f in RUTAS)
open(os.path.join(PUB, 'sitemap.xml'), 'w', encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n')
open(os.path.join(PUB, 'robots.txt'), 'w', encoding='utf-8').write(
    'User-agent: *\nAllow: /\nDisallow: /api/\n\n'
    f'Sitemap: {DOMINIO}/sitemap.xml\n')
print(f'✔ robots.txt + sitemap.xml ({len(RUTAS)} URLs: {n_cursos} cursos + {len(RUTAS)-n_cursos} rutas)')
