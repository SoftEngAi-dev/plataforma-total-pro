#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
command -v python3 >/dev/null || { echo "[ERROR] Python 3.10+ requerido"; exit 1; }
command -v node >/dev/null || { echo "[ERROR] Node.js LTS requerido"; exit 1; }
[[ -d .venv ]] || python3 -m venv .venv
source .venv/bin/activate
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
python3 scripts/ensure_content.py
cd web
[[ -d node_modules ]] || npm install --no-audit --no-fund
npm run build:local
cd ..
if command -v xdg-open >/dev/null; then xdg-open http://127.0.0.1:8787/ >/dev/null 2>&1 || true
elif command -v open >/dev/null; then open http://127.0.0.1:8787/ >/dev/null 2>&1 || true
fi
python local_server.py --port 8787
