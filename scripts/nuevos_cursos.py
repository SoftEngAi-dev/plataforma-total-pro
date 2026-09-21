#!/usr/bin/env python3
"""🏗️ Motor de expansión: data1-4 → web JSONs + indice.json + contenido_f.py (desktop). Idempotente."""
import json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from cursos_nuevos_data1 import NUEVOS as N1
from cursos_nuevos_data2 import NUEVOS as N2
from cursos_nuevos_data3 import NUEVOS as N3
from cursos_nuevos_data4 import NUEVOS as N4

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DATA = RAIZ / "web" / "public" / "data"
TODOS = N1 + N2 + N3 + N4

# ① JSON por curso (formato web: {n, free, lecciones:[{t,x,q}]})
for c in TODOS:
    lecciones = []
    for lec in c["lecciones"]:
        lecciones.append({"t": lec["t"], "x": lec["x"], "q": lec["q"]})
    (DATA / "cursos" / f'{c["slug"]}.json').write_text(
        json.dumps({"n": c["n"], "free": c["free"], "lecciones": lecciones},
                   ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

# ② indice.json (append si no está)
indice = json.loads((DATA / "indice.json").read_text(encoding="utf-8"))
existentes = {c["s"] for c in indice}
agregados = 0
for c in TODOS:
    if c["slug"] not in existentes:
        indice.append({"s": c["slug"], "n": c["n"], "free": c["free"], "l": len(c["lecciones"])})
        agregados += 1
(DATA / "indice.json").write_text(json.dumps(indice, ensure_ascii=False, indent=1), encoding="utf-8")

# ③ contenido_f.py (desktop): CURSOS_MOD = { nombre: [ [t, cc, [[p, ops, ok, exp], …]], …] }
import pprint
mod = {}
for c in TODOS:
    mod[c["n"]] = [[lec["t"], lec["x"],
                    [[q["p"], q["ops"], q["ok"], q["exp"]] for q in lec["q"]]]
                   for lec in c["lecciones"]]
lit = pprint.pformat(mod, width=110)   # literal Python nativo (maneja True/None/quotes)
(RAIZ / "contenido_f.py").write_text(
    '# -*- coding: utf-8 -*-\n'
    '"""🧩 contenido_f — Expansión 2026: matemáticas, lógica y tecnología moderna/emergente.\n'
    'Generado por scripts/nuevos_cursos.py desde la fuente única web. NO editar a mano."""\n\n'
    f'CURSOS_MOD = {lit}\n', encoding="utf-8")

print(f"✔ {len(TODOS)} cursos escritos ({agregados} nuevos en índice) → total índice: {len(indice)}")
print(f"✔ contenido_f.py: {len(mod)} cursos ({(RAIZ / 'contenido_f.py').stat().st_size // 1024} KB)")
for c in TODOS:
    print(f"  {'🆓' if c['free'] else '💎'} {c['slug']}: {len(c['lecciones'])} lecciones, {sum(len(l['q']) for l in c['lecciones'])} quizzes")
