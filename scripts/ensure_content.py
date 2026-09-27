#!/usr/bin/env python3
"""Generate and validate the canonical web curriculum cache."""
from __future__ import annotations
import argparse,json,re,sys,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
import contenido_a,contenido_b,contenido_c,contenido_d,contenido_e,contenido_f
CURSOS={}
for m in (contenido_a,contenido_b,contenido_c,contenido_d,contenido_e,contenido_f): CURSOS.update(m.CURSOS_MOD)
FREE=set(list(CURSOS.keys())[:15])|{"📐 Matemáticas para Programadores — Las que Sí Se Usan","🧠 Lógica y Pensamiento Computacional"}
def slug(v):
 v=unicodedata.normalize("NFKD",v).encode("ascii","ignore").decode()
 return re.sub(r"[^a-z0-9]+","-",v.lower()).strip("-")
def qnorm(q):
 if isinstance(q,dict): return {"p":str(q.get("p","")),"ops":list(q.get("ops",[])),"ok":int(q.get("ok",0)),"exp":str(q.get("exp",""))}
 return {"p":str(q[0]),"ops":list(q[1]),"ok":int(q[2]) if len(q)>2 and isinstance(q[2],int) else 0,"exp":str(q[3]) if len(q)>3 else ""}
def generate(check=False):
 root=ROOT/"web"/"public"/"data"; courses=root/"cursos"; courses.mkdir(parents=True,exist_ok=True)
 items=list(CURSOS.items()); idx=[]; corpus_l=[]; corpus_q=[]; free=[]
 for i,(name,lessons) in enumerate(items):
  clean=re.sub(r"^[^\wÁÉÍÓÚáéíóúÑñüÜ]+","",name).strip(); s=f"{i+1:02d}-{slug(clean)[:40]}"; isfree=name in FREE
  out=[]
  for j,tup in enumerate(lessons):
   qs=[qnorm(x) for x in (tup[2] if len(tup)>2 else [])]; out.append({"t":tup[0],"x":tup[1],"q":qs})
   corpus_l.append({"c":clean,"ci":i,"j":j,"t":str(tup[0]),"x":str(tup[1])[:1800]})
   for q in qs:
    if 0<=q["ok"]<len(q["ops"]): corpus_q.append({"c":clean,"ci":i,"j":j,"t":str(tup[0]),"p":q["p"],"r":q["ops"][q["ok"]],"e":q["exp"]})
  idx.append({"s":s,"n":clean,"free":isfree,"l":len(out)})
  if isfree: free.append(s)
 stats=(len(idx),sum(x["l"] for x in idx),len(corpus_q))
 if stats!=(57,329,658): raise SystemExit(f"ERROR currículo: {stats}; esperado 57/329/658")
 changed=[]
 def put(p,obj):
  text=json.dumps(obj,ensure_ascii=False,separators=(",",":"))+"\n"; old=p.read_text(encoding="utf-8") if p.exists() else None
  if old!=text:
   changed.append(str(p.relative_to(ROOT)))
   if not check: p.write_text(text,encoding="utf-8")
 put(root/"indice.json",idx)
 for i,c in enumerate(idx):
  out=[]; lessons=items[i][1]
  for tup in lessons:
   qs=[qnorm(x) for x in (tup[2] if len(tup)>2 else [])]
   out.append({"t":tup[0],"x":tup[1],"q":qs})
  put(courses/f'{c["s"]}.json',{"n":c["n"],"free":bool(c["free"]),"lecciones":out})
 put(root/"corpus.json",{"v":4,"l":corpus_l,"q":corpus_q})
 put(ROOT/"web"/"public"/"offline-manifest.json",{"version":"5.1.0","free_courses":free,"stats":{"courses":57,"free_courses":len(free),"lessons":329,"quizzes":658}})
 print(f"✅ {'CHECK' if check else 'WRITE'} 57 cursos · {len(free)} FREE · 329 lecciones · 658 quizzes")
 if check and changed: print(*changed,sep="\n"); raise SystemExit(2)
 return changed
if __name__=="__main__":
 ap=argparse.ArgumentParser(); ap.add_argument("--check",action="store_true"); generate(ap.parse_args().check)
