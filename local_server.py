#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Servidor local de Plataforma Total v5.

Sirve web/dist y ofrece una API compatible con la web cloud. Los datos se
guardan fuera del repo. Ollama solo se consulta en localhost.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, mimetypes, os, re, secrets, sqlite3, sys, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT=Path(__file__).resolve().parent
DIST=ROOT/"web"/"dist"; PUBLIC=ROOT/"web"/"public"

def data_dir():
    o=os.environ.get("PT_DATA_DIR")
    if o: p=Path(o).expanduser()
    elif sys.platform.startswith("win"): p=Path(os.environ.get("APPDATA",str(Path.home())))/"PlataformaTotal"
    elif sys.platform=="darwin": p=Path.home()/"Library"/"Application Support"/"PlataformaTotal"
    else: p=Path(os.environ.get("XDG_DATA_HOME",Path.home()/".local"/"share"))/"PlataformaTotal"
    (p/"projects").mkdir(parents=True,exist_ok=True); return p
DATA=data_dir(); DB=DATA/"plataforma.db"
SCHEMA="""
CREATE TABLE IF NOT EXISTS users(alias TEXT PRIMARY KEY,hash TEXT NOT NULL,salt TEXT NOT NULL,creado TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,alias TEXT NOT NULL,expira TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS progreso(alias TEXT PRIMARY KEY,data TEXT NOT NULL,actualizado TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS certificados(codigo TEXT PRIMARY KEY,alias TEXT NOT NULL,curso TEXT NOT NULL,fecha TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS pro(email TEXT PRIMARY KEY,estado INTEGER DEFAULT 1,order_id TEXT,evento TEXT,actualizado TEXT);
CREATE TABLE IF NOT EXISTS pro_alias(alias TEXT PRIMARY KEY,email TEXT,actualizado TEXT);
CREATE TABLE IF NOT EXISTS intentos(alias TEXT PRIMARY KEY,n INTEGER DEFAULT 0,ts TEXT);
CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY,alias TEXT,name TEXT NOT NULL,path TEXT NOT NULL,created TEXT NOT NULL,updated TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_sessions_alias ON sessions(alias);
CREATE INDEX IF NOT EXISTS idx_sessions_expira ON sessions(expira);
CREATE INDEX IF NOT EXISTS idx_certificados_alias ON certificados(alias);
CREATE INDEX IF NOT EXISTS idx_pro_alias_email ON pro_alias(email);
"""
def db():
    c=sqlite3.connect(DB); c.executescript(SCHEMA); return c
def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def pbk(pin,salt): return hashlib.pbkdf2_hmac("sha256",pin.encode(),bytes.fromhex(salt),100000).hex()
def alias_ok(a): return bool(re.fullmatch(r"[a-z0-9_]{3,24}",a or ""))
def merge(a,b):
    a,b=a or {},b or {}; le=dict(a.get("leidas") or {})
    for k,v in (b.get("leidas") or {}).items(): le[k]=sorted(set(le.get(k,[]))|set(v or []))
    last=max([x for x in (a.get("ultima"),b.get("ultima")) if x],key=lambda x:int(x.get("at",0)),default=None)
    return {**a,**b,"leidas":le,
      "completados":sorted(set(a.get("completados",[]))|set(b.get("completados",[]))),
      "xp":max(int(a.get("xp",0)),int(b.get("xp",0))),
      "quiz_ok":max(int(a.get("quiz_ok",0)),int(b.get("quiz_ok",0))),
      "quiz_tot":max(int(a.get("quiz_tot",0)),int(b.get("quiz_tot",0))),
      "racha":{"n":max(int((a.get("racha") or {}).get("n",0)),int((b.get("racha") or {}).get("n",0))),
               "ultimo":(a.get("racha") or {}).get("ultimo") or (b.get("racha") or {}).get("ultimo")},
      "ultima":last,"updated_at":now()}
CORPUS=None
def corpus():
    global CORPUS
    if CORPUS is None:
        p=next((x for x in (DIST/"data"/"corpus.json",PUBLIC/"data"/"corpus.json") if x.exists()),None)
        CORPUS=json.loads(p.read_text(encoding="utf-8")) if p else {"l":[]}
    return CORPUS
STOP=set("de la el los las un una en por para con sin sobre entre como más mas muy si no al del lo le les su sus tu tus mi mis es son sea ser fue que a o u y e ni ya pero cuando dónde donde cómo cual cuál quien quién hay hacer puedo puede puedes tengo tiene tienen me te se nos".split())
def toks(s): return [x for x in re.sub(r"[^a-z0-9+#. ]"," ",(s or "").lower()).replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").split() if len(x)>1 and x not in STOP]
def local_tutor(q):
    qs=set(toks(q)); hits=[]
    for i,x in enumerate(corpus().get("l",[])):
        w=set(toks(str(x.get("t",""))+" "+str(x.get("c",""))+" "+str(x.get("x","")))); sc=len(qs&w)
        if sc: hits.append((sc,i,x))
    hits.sort(reverse=True,key=lambda z:z[0])
    if not hits: return "🏠 Tutor local: no encontré ese concepto en la currícula."
    x=hits[0][2]; return f"📖 {x.get('t','Lección')}\n\n{str(x.get('x',''))[:1400]}"
def ollama(messages):
    if os.environ.get("PT_DISABLE_OLLAMA")=="1": return None
    base=os.environ.get("PT_OLLAMA_URL","http://127.0.0.1:11434").rstrip("/")
    model=os.environ.get("PT_OLLAMA_MODEL")
    try:
        if not model:
            with urllib.request.urlopen(base+"/api/tags",timeout=2) as r:
                ms=json.loads(r.read().decode()).get("models") or []; model=ms[0].get("name") if ms else None
        if not model: return None
        body=json.dumps({"model":model,"messages":messages[-20:],"stream":False,"options":{"temperature":0.3}}).encode()
        req=urllib.request.Request(base+"/api/chat",data=body,headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req,timeout=60) as r: return json.loads(r.read().decode()).get("message",{}).get("content")
    except Exception: return None
class Handler(BaseHTTPRequestHandler):
    server_version="PlataformaTotalLocal/5.0"
    def log_message(self,fmt,*args): sys.stderr.write("[%s] %s\n"%(dt.datetime.now().strftime("%H:%M:%S"),fmt%args))
    def js(self,o,status=200):
        b=json.dumps(o,ensure_ascii=False).encode(); self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(b))); self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(b)
    def body(self):
        n=min(int(self.headers.get("Content-Length","0") or 0),300000); return json.loads(self.rfile.read(n).decode() or "{}") if n else {}
    def auth(self):
        t=self.headers.get("X-Token","")
        if len(t)<32: return None
        c=db(); r=c.execute("SELECT alias,expira FROM sessions WHERE token=?",(t,)).fetchone(); c.close()
        return r[0] if r and r[1]>now() else None
    def do_OPTIONS(self):
        self.send_response(204); self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Headers","Content-Type, X-Token"); self.send_header("Access-Control-Allow-Methods","GET,POST,DELETE,OPTIONS"); self.end_headers()
    def do_GET(self):
        u=urlparse(self.path); p=u.path
        if p.startswith("/api/"):
            q=parse_qs(u.query)
            if p=="/api/health":
                return self.js({"ok":True,"version":"5.0.0","mode":"local","db":str(DB)})
            if p=="/api/system":
                m=None
                try:
                    base=os.environ.get("PT_OLLAMA_URL","http://127.0.0.1:11434")
                    with urllib.request.urlopen(base.rstrip("/")+"/api/tags",timeout=1.5) as r: m=(json.loads(r.read().decode()).get("models") or [{}])[0].get("name")
                except Exception: pass
                return self.js({"ok":True,"mode":"local","version":"5.0.0","data_dir":str(DATA),"db":str(DB),"ollama":bool(m),"ollama_model":m})
            if p=="/api/progreso":
                a=self.auth()
                if not a:return self.js({"ok":False,"error":"sesión inválida"},401)
                c=db(); r=c.execute("SELECT data FROM progreso WHERE alias=?",(a,)).fetchone(); c.close()
                return self.js({"ok":True,"data":json.loads(r[0]) if r else None})
            if p=="/api/pro":
                a=self.auth()
                if not a:return self.js({"ok":False,"error":"sesión inválida"},401)
                c=db(); r=c.execute("SELECT p.estado FROM pro_alias pa JOIN pro p ON p.email=pa.email WHERE pa.alias=?",(a,)).fetchone(); c.close()
                return self.js({"ok":True,"pro":bool(r and r[0]==1) or os.environ.get("PT_LOCAL_PRO")=="1"})
            if p=="/api/certificado":
                code=(q.get("codigo",[""])[0] or "").strip().upper(); code=code if code.startswith("PT-") else "PT-"+code
                c=db(); r=c.execute("SELECT alias,curso,fecha FROM certificados WHERE codigo=?",(code,)).fetchone(); c.close()
                if not r:return self.js({"ok":True,"valido":False})
                return self.js({"ok":True,"valido":True,"quien":r[0][:3]+"***","curso":r[1],"fecha":r[2]})
            if p=="/api/projects":
                a=self.auth() or "local"; c=db(); rs=c.execute("SELECT id,name,path,created,updated FROM projects WHERE alias=? ORDER BY updated DESC",(a,)).fetchall(); c.close()
                return self.js({"ok":True,"projects":[dict(id=r[0],name=r[1],path=r[2],created=r[3],updated=r[4]) for r in rs]})
            return self.js({"ok":False,"error":"endpoint no encontrado"},404)
        self.static(p)
    def do_POST(self):
        p=urlparse(self.path).path
        if not p.startswith("/api/"):return self.send_error(404)
        if p=="/api/auth":
            b=self.body(); a=str(b.get("alias","")).strip().lower(); pin=str(b.get("pin",""))
            if not alias_ok(a) or len(pin)<4:return self.js({"ok":False,"error":"alias 3-24 y PIN 4+"},400)
            c=db(); r=c.execute("SELECT hash,salt FROM users WHERE alias=?",(a,)).fetchone()
            if r and not secrets.compare_digest(pbk(pin,r[1]),r[0]): c.close(); return self.js({"ok":False,"error":"PIN incorrecto"},401)
            if not r:
                salt=secrets.token_hex(16); c.execute("INSERT INTO users VALUES(?,?,?,?)",(a,pbk(pin,salt),salt,now()))
            token=secrets.token_hex(32); exp=(dt.datetime.now(dt.timezone.utc)+dt.timedelta(days=30)).isoformat(); c.execute("INSERT INTO sessions VALUES(?,?,?)",(token,a,exp)); c.commit(); c.close()
            return self.js({"ok":True,"alias":a,"token":token})
        a=self.auth()
        if p in ("/api/progreso","/api/pro") and not a:return self.js({"ok":False,"error":"sesión inválida"},401)
        if p=="/api/progreso":
            incoming=self.body().get("data") or {}; c=db(); r=c.execute("SELECT data FROM progreso WHERE alias=?",(a,)).fetchone(); cur=json.loads(r[0]) if r else {}; m=merge(cur,incoming)
            c.execute("INSERT INTO progreso VALUES(?,?,?) ON CONFLICT(alias) DO UPDATE SET data=excluded.data,actualizado=excluded.actualizado",(a,json.dumps(m,ensure_ascii=False),now())); c.commit(); c.close(); return self.js({"ok":True,"data":m})
        if p=="/api/pro":
            em=str(self.body().get("email","")).strip().lower()
            allowed=os.environ.get("PT_LOCAL_PRO")=="1" or em in {x.strip().lower() for x in os.environ.get("PT_LOCAL_PRO_EMAILS","").split(",") if x.strip()}
            c=db()
            if allowed: c.execute("INSERT INTO pro(email,estado,actualizado) VALUES(?,?,?) ON CONFLICT(email) DO UPDATE SET estado=1,actualizado=excluded.actualizado",(em or "local@localhost",1,now()))
            r=c.execute("SELECT estado FROM pro WHERE email=?",(em,)).fetchone() if em else None
            if not (allowed or (r and r[0]==1)):c.close();return self.js({"ok":False,"pro":False,"error":"email sin PRO local"},404)
            c.execute("INSERT INTO pro_alias VALUES(?,?,?) ON CONFLICT(alias) DO UPDATE SET email=excluded.email,actualizado=excluded.actualizado",(a,em or "local@localhost",now()));c.commit();c.close();return self.js({"ok":True,"pro":True})
        if p=="/api/admin":
            b=self.body()
            if b.get("secret")!=os.environ.get("PT_ADMIN_SECRET"):return self.js({"ok":False,"error":"no autorizado"},401)
            em=str(b.get("email","")).strip().lower(); st=0 if str(b.get("accion","pro"))=="quitar" else 1; c=db(); c.execute("INSERT INTO pro(email,estado,evento,actualizado) VALUES(?,?,?,?) ON CONFLICT(email) DO UPDATE SET estado=excluded.estado,evento=excluded.evento,actualizado=excluded.actualizado",(em,st,"local_admin",now()));c.commit();c.close();return self.js({"ok":True,"estado":st,"email":em})
        if p=="/api/certificado":
            if not a:return self.js({"ok":False,"error":"sesión inválida"},401)
            b=self.body(); code=str(b.get("codigo","")).strip().upper(); code=code if code.startswith("PT-") else "PT-"+code; curso=str(b.get("curso","")).strip()
            if not re.fullmatch(r"PT-[A-Z0-9-]{3,20}",code) or not curso:return self.js({"ok":False,"error":"certificado inválido"},400)
            c=db();c.execute("INSERT OR IGNORE INTO certificados VALUES(?,?,?,?)",(code,a,curso,dt.date.today().isoformat()));c.commit();c.close();return self.js({"ok":True,"codigo":code})
        if p=="/api/chat":
            b=self.body(); r=ollama(b.get("messages") or [])
            if r:return self.js({"ok":True,"respuesta":r,"backend":"ollama"})
            last=next((m.get("content","") for m in reversed(b.get("messages") or []) if m.get("role")=="user"),"")
            return self.js({"ok":True,"respuesta":local_tutor(last),"backend":"local-rag"})
        if p=="/api/projects":
            a=a or "local"; b=self.body(); name=str(b.get("name","")).strip() or "Proyecto sin nombre"; pid=secrets.token_hex(8); pth=DATA/"projects"/pid; pth.mkdir(parents=True,exist_ok=True); (pth/"README.md").write_text("# "+name+"\n\nProyecto creado en Plataforma Total.\n",encoding="utf-8")
            t=now();c=db();c.execute("INSERT INTO projects VALUES(?,?,?,?,?,?)",(pid,a,name,str(pth),t,t));c.commit();c.close();return self.js({"ok":True,"project":{"id":pid,"name":name,"path":str(pth),"created":t,"updated":t}},201)
        return self.js({"ok":False,"error":"endpoint no encontrado"},404)
    def do_DELETE(self):
        u=urlparse(self.path); 
        if u.path!="/api/projects":return self.js({"ok":False,"error":"endpoint no encontrado"},404)
        a=self.auth() or "local"; pid=parse_qs(u.query).get("id",[""])[0];c=db();r=c.execute("SELECT alias FROM projects WHERE id=?",(pid,)).fetchone()
        if not r or r[0] not in (a,"local"):c.close();return self.js({"ok":False,"error":"proyecto no encontrado"},404)
        c.execute("DELETE FROM projects WHERE id=?",(pid,));c.commit();c.close();return self.js({"ok":True})
    def static(self,path):
        rel=path.lstrip("/") or "index.html"; candidates=[DIST/rel,DIST/rel/"index.html"]
        target=next((x for x in candidates if x.is_file()),None)
        if not target:return self.send_error(404,"Archivo no encontrado")
        b=target.read_bytes();self.send_response(200);self.send_header("Content-Type",mimetypes.guess_type(str(target))[0] or "application/octet-stream");self.send_header("Content-Length",str(len(b)));self.send_header("Cache-Control","no-cache");self.end_headers();self.wfile.write(b)
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--host",default=os.environ.get("PT_HOST","127.0.0.1"));ap.add_argument("--port",type=int,default=int(os.environ.get("PT_PORT","8787")));a=ap.parse_args();db().close()
    if not DIST.exists():raise SystemExit("Falta web/dist. Ejecutá npm run build:local dentro de web.")
    print(f"🎓 Plataforma Total v5 → http://{a.host}:{a.port}\n💾 Datos → {DB}")
    ThreadingHTTPServer((a.host,a.port),Handler).serve_forever()
if __name__=="__main__":main()
