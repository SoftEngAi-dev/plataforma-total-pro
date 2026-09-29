#!/usr/bin/env python3
"""📴 Guardia Offline — impide que NINGÚN cambio futuro rompa el contrato
"17 cursos gratis 100% offline al instalar la PWA".
Corre sin red, en segundos. Exit 0 = contrato íntegro; exit 1 = roto (bloquea el push).
"""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "web" / "public"
errores, ok = [], []

def chequear(cond, msg):
    (ok if cond else errores).append(("✔ " if cond else "✗ ") + msg)

sw = (PUB / "sw.js").read_text(encoding="utf-8")
chequear(re.search(r"\bd\.core\b", sw), "sw.js lee 'd.core' del manifiesto (precarga de cursos)")
import ast
m = re.search(r"NUCLEO\s*=\s*(\[.*?\]);", sw, re.S)
chequear(bool(m), "sw.js define NUCLEO")
try:
    nucleo = ast.literal_eval(m.group(1)) if m else []
except Exception:
    nucleo, chequear(False, "NUCLEO no parsea como lista literal")
    nucleo = []
for p in nucleo:
    if p:  # '' es la raíz
        chequear((PUB / p).exists(), f"núcleo SW existe en disco: {p} ({len(nucleo)} en total)")

mani_path = PUB / "offline-manifest.json"
chequear(mani_path.exists(), "offline-manifest.json existe")
man = json.loads(mani_path.read_text(encoding="utf-8"))
core = man.get("core", [])
free = man.get("free_courses", [])
chequear(bool(core), "manifiesto tiene lista 'core'")
chequear(len(free) == 17, f"17 cursos gratis declarados (hay {len(free)})")
chequear(len(core) == len(free) + 1, f"core = 1 lector + {len(free)} cursos (hay {len(core)})")
chequear(core and core[0] == "aprender", "core[0] = página lector 'aprender'")
chequear((ROOT / "web" / "src" / "pages" / "aprender.astro").exists(), "aprender.astro existe (el lector)")
for item in core[1:]:
    chequear(item.startswith("data/cursos/") and item.endswith(".json"), f"forma URL core: {item}")
    chequear((PUB / item).exists(), f"existe en disco: {item}")
idx = json.loads((PUB / "data" / "indice.json").read_text(encoding="utf-8"))
chequear(len(idx if isinstance(idx, list) else idx.get("cursos", [])) == 57, "índice tiene 57 cursos")
slugs_idx = {c["s"] for c in (idx if isinstance(idx, list) else idx.get("cursos", []))}
faltan = [s for s in free if s not in slugs_idx]
chequear(not faltan, "todos los slugs gratis existen en el índice")

errores_unicos = list(dict.fromkeys(errores))  # mensajes repetidos por archivo → resume
print("\n".join(dict.fromkeys(ok)))
if errores_unicos:
    print("\n".join(errores_unicos[:10]))
    print(f"\n🔴 CONTRATO OFFLINE ROTO ({len(errores)} fallas) — no publiques hasta arreglarlo")
    sys.exit(1)
print(f"\n🟢 CONTRATO OFFLINE ÍNTEGRO: {len(nucleo)} núcleo + {len(core)} core precargables → 100% offline al instalar")
