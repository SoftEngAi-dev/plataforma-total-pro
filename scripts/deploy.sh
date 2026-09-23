#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# 🚀 scripts/deploy.sh — Despliegue IDEMPOTENTE y a prueba de fósiles
#
# Uso:
#   CLOUDFLARE_API_TOKEN=… CLOUDFLARE_ACCOUNT_ID=… GH_TOKEN=… bash scripts/deploy.sh [--push]
#
# Qué hace (en orden, aborta al menor fallo):
#   1. fetch + reset --hard FETCH_HEAD (nunca build sobre árbol fósil/snapshot viejo)
#   2. sentinel: exige "57 cursos" en el índice y en src (evita regresiones de contenido)
#   3. node_modules presente (si no, instala)
#   4. build raíz → deploy CF → verifica PRODUCCIÓN en vivo (versión, curso/57, sitemap=68)
#   5. build espejo → regenera docs/app
#   6. con --push: commitea docs/app/pontenciales cambios y empuja; sin flag: deja todo preparado
#
# Principio: si algo no coincide, NO ESTARÁS en producción rota — el script muere antes.
# ═══════════════════════════════════════════════════════════════════════════
set -euo pipefail
cd "$(dirname "$0")/.."
RAIZ=$(pwd)
: "${CLOUDFLARE_API_TOKEN:?exportá CLOUDFLARE_API_TOKEN}"
: "${CLOUDFLARE_ACCOUNT_ID:?exportá CLOUDFLARE_ACCOUNT_ID}"
: "${GH_TOKEN:?exportá GH_TOKEN (PAT con repo)}"
REPO_URL="https://SoftEngAi-dev:${GH_TOKEN}@github.com/SoftEngAi-dev/plataforma-total-pro.git"
PROD="https://plataforma-total-web.pages.dev"

echo "① sincronizando con remoto (anti-fósil)…"
git clean -fdq -e web/node_modules -e web/.wrangler -e web/.dev.vars
git fetch "$REPO_URL" main -q
git reset --hard FETCH_HEAD -q
HEAD=$(git rev-parse --short HEAD); echo "   HEAD=$HEAD"

echo "② sentinel de contenido…"
N=$(python3 -c "import json;print(len(json.load(open('web/public/data/indice.json'))))")
[ "$N" = "57" ] || { echo "❌ índice con $N cursos (esperaba 57) — aborto"; exit 1; }
grep -q "57 cursos" web/src/pages/index.astro || { echo "❌ index.astro sin '57 cursos' — aborto"; exit 1; }
echo "   ✔ 57 cursos en índice y home"

echo "③ dependencias…"
[ -d web/node_modules ] || (cd web && npm install --no-audit --no-fund > /dev/null)
echo "   ✔ node_modules"

echo "④ build raíz + deploy CF…"
(cd web && ASTRO_BASE=/ npm run build 2>&1 | grep -c "Complete!")
[ -f web/dist/index.html ] || { echo "❌ build sin dist/index.html"; exit 1; }
(cd web && npx wrangler pages deploy dist --project-name plataforma-total-web 2>&1 | tail -1)

echo "⑤ verificación de producción en vivo (20 s de propagación)…"
sleep 20
V=$(curl -s "$PROD/" | grep -oE 'v4\.9\.[0-9]+' | head -1)
C57=$(curl -s -o /dev/null -w '%{http_code}' "$PROD/curso/57")
SM=$(curl -s "$PROD/sitemap.xml" | grep -oc '<url>')
OG=$(curl -s -o /dev/null -w '%{http_code}' "$PROD/og-cover.png")
LL=$(curl -s -o /dev/null -w '%{http_code}' "$PROD/llms.txt")
echo "   versión=$V · curso/57=$C57 · sitemap=$SM urls · og-cover=$OG · llms.txt=$LL"
[ "$C57" = "200" ] && [ "$SM" = "68" ] && [ "$OG" = "200" ] || { echo "❌ producción rota tras deploy — INVESTIGAR antes de seguir"; exit 1; }

echo "⑥ build espejo GitHub Pages + docs/app…"
(cd web && ASTRO_BASE=/plataforma-total-pro/app/ npm run build 2>&1 | grep -c "Complete!")
rm -rf docs/app && mkdir -p docs/app && cp -r web/dist/plataforma-total-pro/app/. docs/app/
touch docs/.nojekyll
echo "   ✔ docs/app regenerado"

if [ "${1:-}" = "--push" ]; then
  echo "⑦ commit + push…"
  git add -A
  git -c user.name="SoftEngAi Dev" -c user.email="dev@softengai.dev" \
      commit -m "🚀 deploy idempotente ($HEAD)" || echo "   (sin cambios que commitear)"
  git push "$REPO_URL" main 2>&1 | tail -1
else
  echo "⑦ sin --push: docs/app quedó preparado en el árbol de trabajo."
fi
echo "✅ DEPLOY COMPLETO Y VERIFICADO — $PROD ($V)"
