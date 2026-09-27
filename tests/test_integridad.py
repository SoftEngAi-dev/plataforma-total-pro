#!/usr/bin/env python3
"""Integridad de Plataforma Total v5."""
import json, os, sys, py_compile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; os.chdir(ROOT); sys.path.insert(0,str(ROOT))
def main():
    cursos={}
    for nombre in ("contenido_a","contenido_b","contenido_c","contenido_d","contenido_e","contenido_f"):
        cursos.update(__import__(nombre).CURSOS_MOD)
    assert len(cursos)==57, f"cursos={len(cursos)}"
    lecciones=sum(len(v) for v in cursos.values()); quizzes=0
    for curso,ls in cursos.items():
        assert ls, f"{curso}: sin lecciones"
        for i,lec in enumerate(ls,1):
            assert len(lec)>=3 and lec[0] and lec[1], f"{curso} L{i}"
            qs=lec[2]; assert qs and len(qs)>=2, f"{curso} L{i}: quizzes insuficientes"
            for j,q in enumerate(qs,1):
                assert q[0] and len(q[1])==4 and isinstance(q[2],int) and 0<=q[2]<4 and q[3], f"{curso} L{i} Q{j}"
                quizzes+=1
    assert lecciones==329, f"lecciones={lecciones}"
    assert quizzes==658, f"quizzes={quizzes}"
    idx=json.loads((ROOT/"web/public/data/indice.json").read_text(encoding="utf-8"))
    assert len(idx)==57 and sum(x["l"] for x in idx)==329 and sum(1 for x in idx if x["free"])==17
    for f in ("main.py","contenido_a.py","contenido_b.py","contenido_c.py","contenido_d.py","contenido_e.py","local_server.py"): py_compile.compile(f,doraise=True)
    print(f"OK: {len(cursos)} cursos / {lecciones} lecciones / {quizzes} quizzes")
if __name__=="__main__": main()
