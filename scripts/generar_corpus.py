#!/usr/bin/env python3
"""🏗️ Genera web/public/data/corpus.json — el cerebro del Tutor Propio.
Recorre data/indice.json + data/cursos/*.json y emite chunks (lección + quiz)
con nombres de campo mínimos para que el navegador lo cargue rápido."""
import json, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent / "web" / "public" / "data"
indice = json.loads((RAIZ / "indice.json").read_text(encoding="utf-8"))

lecciones, quizzes = [], []
recorte = lambda s: s if len(s) <= 1600 else s[:1600] + "…"

for ci, cur in enumerate(indice):
    ruta = RAIZ / "cursos" / (cur["s"] + ".json")
    if not ruta.exists():
        print("⚠ falta", ruta.name); continue
    d = json.loads(ruta.read_text(encoding="utf-8"))
    for j, lec in enumerate(d.get("lecciones", [])):
        x = recorte((lec.get("x") or "").strip())
        if x or lec.get("t"):
            lecciones.append({"c": d["n"], "ci": ci, "j": j, "t": (lec.get("t") or "").strip(), "x": x})
        for q in lec.get("q", []):
            ops = q.get("ops", []); ok = q.get("ok", 0)
            if 0 <= ok < len(ops):
                quizzes.append({"c": d["n"], "ci": ci, "j": j, "t": lec.get("t", ""),
                                "p": q.get("p", ""), "r": ops[ok], "e": q.get("exp", "")})

salida = {"v": 3, "l": lecciones, "q": quizzes}
(RAIZ / "corpus.json").write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
kb = (RAIZ / "corpus.json").stat().st_size / 1024
print(f"✔ corpus.json: {len(lecciones)} lecciones + {len(quizzes)} preguntas quiz → {kb:.0f} KB")
