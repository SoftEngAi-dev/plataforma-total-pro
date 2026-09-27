#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runtime Local First de Plataforma Total.

Conecta:
- currículo real de contenido_a.py ... contenido_f.py
- JSON web como cache
- SQLite web para cuentas
- SQLite desktop para progreso compartido
- proyectos desktop/web en la misma carpeta
- Ollama local opcional
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import mimetypes
import os
import re
import secrets
import shutil
import sqlite3
import sys
import unicodedata
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "web" / "dist"
PUBLIC = ROOT / "web" / "public"

sys.path.insert(0, str(ROOT))
from contenido_a import CURSOS_MOD as _A
from contenido_b import CURSOS_MOD as _B
from contenido_c import CURSOS_MOD as _C
from contenido_d import CURSOS_MOD as _D
from contenido_e import CURSOS_MOD as _E
from contenido_f import CURSOS_MOD as _F

CURSOS = {}
for _mod in (_A, _B, _C, _D, _E, _F):
    CURSOS.update(_mod)
COURSE_NAMES = list(CURSOS.keys())
NAME_TO_INDEX = {name: i for i, name in enumerate(COURSE_NAMES)}
FREE_COURSES = set(COURSE_NAMES[:15])
FREE_COURSES.update(n for n in COURSE_NAMES if n.startswith("📐 Matemáticas") or n.startswith("🧠 Lógica"))

def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

def course_slug(index: int, name: str) -> str:
    return f"{index + 1:02d}-{slugify(name)[:40]}"

SLUG_TO_INDEX = {course_slug(i, n): i for i, n in enumerate(COURSE_NAMES)}

def catalog_payload() -> list[dict]:
    return [
        {"s": course_slug(i, name), "n": name, "free": name in FREE_COURSES, "l": len(CURSOS[name])}
        for i, name in enumerate(COURSE_NAMES)
    ]

def load_catalog() -> list[dict]:
    p = PUBLIC / "data" / "indice.json"
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if len(data) == len(COURSE_NAMES) and sum(int(x.get("l", 0)) for x in data) == sum(len(v) for v in CURSOS.values()):
                return data
        except Exception:
            pass
    return catalog_payload()

def course_payload(index: int) -> dict:
    name = COURSE_NAMES[index]
    return {
        "n": name,
        "free": name in FREE_COURSES,
        "lecciones": [
            {
                "t": title,
                "x": text,
                "q": [{"p": q[0], "ops": list(q[1]), "ok": int(q[2]), "exp": q[3]} for q in quizzes],
            }
            for title, text, quizzes in CURSOS[name]
        ],
    }

def load_course(slug: str) -> dict | None:
    index = SLUG_TO_INDEX.get(slug)
    if index is None:
        return None
    for root in (DIST, PUBLIC):
        p = root / "data" / "cursos" / f"{slug}.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
    return course_payload(index)

CORPUS = None

def get_corpus() -> dict:
    global CORPUS
    if CORPUS is not None:
        return CORPUS
    for root in (DIST, PUBLIC):
        p = root / "data" / "corpus.json"
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if len(data.get("l", [])) >= sum(len(v) for v in CURSOS.values()):
                    CORPUS = data
                    return CORPUS
            except Exception:
                pass
    lessons, quizzes = [], []
    for ci, name in enumerate(COURSE_NAMES):
        for j, row in enumerate(CURSOS[name]):
            lessons.append({"c": name, "ci": ci, "j": j, "t": row[0], "x": row[1][:1800]})
            for q in row[2]:
                quizzes.append({"c": name, "ci": ci, "j": j, "t": row[0], "p": q[0], "r": q[1][q[2]], "e": q[3]})
    CORPUS = {"v": 4, "l": lessons, "q": quizzes}
    return CORPUS

def data_root() -> Path:
    override = os.environ.get("PT_DATA_DIR")
    root = Path(override).expanduser() if override else Path.home() / "PlataformaTotal"
    for p in (root, root / "datos", root / "config", root / "proyectos"):
        p.mkdir(parents=True, exist_ok=True)
    return root

APP_DIR = data_root()
DATA_DIR = APP_DIR / "datos"
DB = DATA_DIR / "web.db"
DESKTOP_DB = DATA_DIR / "plataforma.db"
PROJECTS_DIR = APP_DIR / "proyectos"

SCHEMA = """
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

DESKTOP_SCHEMA = """
CREATE TABLE IF NOT EXISTS progreso(curso TEXT,leccion INTEGER,fecha TEXT,PRIMARY KEY(curso,leccion));
CREATE TABLE IF NOT EXISTS quiz_scores(curso TEXT,leccion INTEGER,mejor INTEGER,total INTEGER,fecha TEXT,PRIMARY KEY(curso,leccion));
CREATE TABLE IF NOT EXISTS chats(id INTEGER PRIMARY KEY AUTOINCREMENT,rol TEXT,mensaje TEXT,fecha TEXT);
CREATE TABLE IF NOT EXISTS pomodoros(id INTEGER PRIMARY KEY AUTOINCREMENT,fecha TEXT);
CREATE TABLE IF NOT EXISTS actividad_dias(fecha TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS certificados(id INTEGER PRIMARY KEY AUTOINCREMENT,curso TEXT,alumno TEXT,codigo TEXT,fecha TEXT);
CREATE TABLE IF NOT EXISTS licencia(clave TEXT PRIMARY KEY,meta TEXT,fecha TEXT);
"""

def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()

def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.executescript(SCHEMA)
    return conn

def desktop_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DESKTOP_DB)
    conn.executescript(DESKTOP_SCHEMA)
    return conn

def pbk(pin: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", pin.encode(), bytes.fromhex(salt), 100000).hex()

def alias_ok(alias: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9_]{3,24}", alias or ""))

def merge_quizzes(a: dict | None, b: dict | None) -> dict:
    out = dict(a or {})
    for key, raw in (b or {}).items():
        value = raw or {}
        old = out.get(key)
        if not old:
            out[key] = dict(value)
            continue
        out[key] = {
            "correct": max(int(old.get("correct", 0)), int(value.get("correct", 0))),
            "answered": max(int(old.get("answered", 0)), int(value.get("answered", 0))),
            "total": max(int(old.get("total", 0)), int(value.get("total", 0))),
            "updated_at": max(str(old.get("updated_at", "")), str(value.get("updated_at", ""))) or None,
        }
    return out

def merge_state(a: dict | None, b: dict | None) -> dict:
    a, b = a or {}, b or {}
    leidas = {k: list(v or []) for k, v in (a.get("leidas") or {}).items()}
    for k, v in (b.get("leidas") or {}).items():
        leidas[k] = sorted(set(leidas.get(k, [])) | set(v or []), key=lambda x: int(x))
    quiz_lessons = merge_quizzes(a.get("quiz_lessons"), b.get("quiz_lessons"))
    ultima = [x for x in (a.get("ultima"), b.get("ultima")) if x]
    last = max(ultima, key=lambda x: int(x.get("at", 0))) if ultima else None
    days = sorted(set(a.get("dias_activos") or []) | set(b.get("dias_activos") or []))
    qtot = len(quiz_lessons)
    qok = sum(1 for x in quiz_lessons.values() if int(x.get("total", 0)) > 0 and int(x.get("correct", 0)) >= int(x.get("total", 0)))
    return {
        **a,
        **b,
        "leidas": leidas,
        "quiz_lessons": quiz_lessons,
        "quiz_tot": qtot,
        "quiz_ok": qok,
        "dias_activos": days,
        "completados": sorted(set(a.get("completados") or []) | set(b.get("completados") or [])),
        "xp": max(int(a.get("xp", 0) or 0), int(b.get("xp", 0) or 0)),
        "racha": {
            "n": max(int((a.get("racha") or {}).get("n", 0)), int((b.get("racha") or {}).get("n", 0))),
            "ultimo": (a.get("racha") or {}).get("ultimo") or (b.get("racha") or {}).get("ultimo"),
        },
        "ultima": last,
        "updated_at": now(),
    }

def streak_from_days(days: list[str]) -> int:
    if not days:
        return 0
    values = set(days)
    today = dt.date.today()
    if today.isoformat() not in values:
        today -= dt.timedelta(days=1)
        if today.isoformat() not in values:
            return 0
    n = 0
    while today.isoformat() in values:
        n += 1
        today -= dt.timedelta(days=1)
    return n

def desktop_snapshot() -> dict:
    if not DESKTOP_DB.exists():
        return {}
    conn = desktop_db()
    try:
        leidas: dict[str, list[int]] = {}
        for curso, lesson, _date in conn.execute("SELECT curso,leccion,fecha FROM progreso"):
            ci = NAME_TO_INDEX.get(curso)
            if ci is not None:
                leidas.setdefault(str(ci), []).append(int(lesson))
        for key in leidas:
            leidas[key] = sorted(set(leidas[key]))

        quizzes = {}
        for curso, lesson, best, total, updated in conn.execute("SELECT curso,leccion,mejor,total,fecha FROM quiz_scores"):
            ci = NAME_TO_INDEX.get(curso)
            if ci is not None:
                quizzes[f"{ci}:{int(lesson)}"] = {
                    "correct": int(best), "answered": int(total), "total": int(total), "updated_at": updated
                }

        days = sorted({str(r[0])[:10] for r in conn.execute("SELECT fecha FROM actividad_dias")})
        completed = []
        for ci, name in enumerate(COURSE_NAMES):
            total_lessons = len(CURSOS[name])
            read_count = len(leidas.get(str(ci), []))
            quiz_total = sum(1 for row in CURSOS[name] if row[2])
            quiz_perfect = sum(
                1 for key, q in quizzes.items()
                if key.startswith(f"{ci}:") and int(q["total"]) > 0 and int(q["correct"]) >= int(q["total"])
            )
            if read_count >= total_lessons and quiz_perfect >= quiz_total:
                completed.append(course_slug(ci, name))

        perfect_count = sum(1 for q in quizzes.values() if int(q["total"]) > 0 and int(q["correct"]) >= int(q["total"]))
        lesson_count = sum(len(v) for v in leidas.values())
        xp = lesson_count * 10 + perfect_count * 5 + len(completed) * 50

        last_row = conn.execute("SELECT curso,leccion,fecha FROM progreso ORDER BY fecha DESC LIMIT 1").fetchone()
        ultima = None
        if last_row and last_row[0] in NAME_TO_INDEX:
            ci = NAME_TO_INDEX[last_row[0]]
            j = int(last_row[1])
            stamp = 0
            try:
                stamp = int(dt.datetime.fromisoformat(str(last_row[2]).replace("Z", "+00:00")).timestamp() * 1000)
            except Exception:
                pass
            ultima = {"c": ci, "j": j, "t": CURSOS[last_row[0]][j][0], "at": stamp}

        return {
            "xp": xp,
            "quiz_ok": perfect_count,
            "quiz_tot": len(quizzes),
            "racha": {"n": streak_from_days(days), "ultimo": days[-1] if days else None},
            "dias_activos": days,
            "leidas": leidas,
            "quiz_lessons": quizzes,
            "completados": completed,
            "ultima": ultima,
            "source": "desktop-sqlite",
        }
    finally:
        conn.close()

def write_desktop_state(state: dict) -> None:
    conn = desktop_db()
    try:
        stamp = now()
        for ci_raw, lessons in (state.get("leidas") or {}).items():
            try:
                ci = int(ci_raw)
            except Exception:
                continue
            if not (0 <= ci < len(COURSE_NAMES)):
                continue
            curso = COURSE_NAMES[ci]
            for lesson in lessons or []:
                j = int(lesson)
                if 0 <= j < len(CURSOS[curso]):
                    conn.execute("INSERT OR IGNORE INTO progreso(curso,leccion,fecha) VALUES(?,?,?)", (curso, j, stamp))

        for key, raw in (state.get("quiz_lessons") or {}).items():
            try:
                ci, j = [int(x) for x in str(key).split(":", 1)]
                if not (0 <= ci < len(COURSE_NAMES) and 0 <= j < len(CURSOS[COURSE_NAMES[ci]])):
                    continue
                curso = COURSE_NAMES[ci]
                q = raw or {}
                total = max(1, int(q.get("total", 0)))
                correct = max(0, min(total, int(q.get("correct", 0))))
                old = conn.execute("SELECT mejor,total FROM quiz_scores WHERE curso=? AND leccion=?", (curso, j)).fetchone()
                best = max(int(old[0]), correct) if old else correct
                db_total = max(int(old[1]), total) if old else total
                conn.execute(
                    "INSERT OR REPLACE INTO quiz_scores(curso,leccion,mejor,total,fecha) VALUES(?,?,?,?,?)",
                    (curso, j, best, db_total, str(q.get("updated_at") or stamp)),
                )
            except Exception:
                continue

        for day in state.get("dias_activos") or []:
            conn.execute("INSERT OR IGNORE INTO actividad_dias(fecha) VALUES(?)", (str(day),))
        conn.commit()
    finally:
        conn.close()

def save_progress(alias: str, incoming: dict) -> dict:
    conn = db()
    try:
        row = conn.execute("SELECT data FROM progreso WHERE alias=?", (alias,)).fetchone()
        current = json.loads(row[0]) if row else {}
        merged = merge_state(current, incoming)
        conn.execute(
            "INSERT INTO progreso(alias,data,actualizado) VALUES(?,?,?) "
            "ON CONFLICT(alias) DO UPDATE SET data=excluded.data,actualizado=excluded.actualizado",
            (alias, json.dumps(merged, ensure_ascii=False), merged["updated_at"]),
        )
        conn.commit()
    finally:
        conn.close()
    write_desktop_state(merged)
    return merge_state(merged, desktop_snapshot())

STOP = set("de la el los las un una unos unas en por para con sin sobre entre como más mas muy si no al del lo le les su sus tu tus mi mis es son sea ser fue que a o u y e ni ya pero cuando dónde donde cómo cual cuál quien quién hay hacer puedo puede puedes tengo tiene tienen me te se nos".split())

def tokens(value: str) -> list[str]:
    value = unicodedata.normalize("NFD", (value or "").lower())
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    return [x for x in re.sub(r"[^a-z0-9+#.]", " ", value).split() if len(x) > 1 and x not in STOP]

def local_tutor(query: str) -> str:
    wanted = set(tokens(query))
    if not wanted:
        return "🏠 Tutor local: escribí una pregunta sobre un lenguaje, concepto o curso."
    hits = []
    for item in get_corpus().get("l", []):
        words = set(tokens(f"{item.get('t','')} {item.get('c','')} {item.get('x','')}"))
        score = len(wanted & words)
        if score:
            hits.append((score, item))
    hits.sort(key=lambda x: x[0], reverse=True)
    if not hits:
        return "🏠 Tutor local: no encontré una coincidencia clara en la currícula."
    item = hits[0][1]
    return f"📖 «{item.get('t','Lección')}» · {item.get('c','')}\\n\\n{str(item.get('x',''))[:1800]}"

def ollama(messages: list[dict]) -> str | None:
    if os.environ.get("PT_DISABLE_OLLAMA") == "1":
        return None
    base = os.environ.get("PT_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
    model = os.environ.get("PT_OLLAMA_MODEL")
    try:
        if not model:
            with urllib.request.urlopen(base + "/api/tags", timeout=2) as response:
                models = json.loads(response.read().decode()).get("models") or []
                model = models[0].get("name") if models else None
        if not model:
            return None
        payload = json.dumps({
            "model": model, "messages": messages[-20:], "stream": False,
            "options": {"temperature": 0.3},
        }).encode()
        req = urllib.request.Request(base + "/api/chat", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode()).get("message", {}).get("content")
    except Exception:
        return None

class Handler(BaseHTTPRequestHandler):
    server_version = "PlataformaTotalLocal/5.1"

    def log_message(self, fmt, *args):
        sys.stderr.write(f"[{dt.datetime.now().strftime('%H:%M:%S')}] {fmt % args}\\n")

    def js(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Token")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        size = min(max(int(self.headers.get("Content-Length", "0") or 0), 0), 500_000)
        if not size:
            return {}
        try:
            return json.loads(self.rfile.read(size).decode("utf-8", "replace") or "{}")
        except Exception:
            return {}

    def auth(self):
        token = self.headers.get("X-Token", "")
        if len(token) < 32:
            return None
        conn = db()
        try:
            row = conn.execute("SELECT alias,expira FROM sessions WHERE token=?", (token,)).fetchone()
        finally:
            conn.close()
        return row[0] if row and row[1] > now() else None

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Token")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path.startswith("/api/"):
            if path == "/api/health":
                idx = load_catalog()
                return self.js({
                    "ok": True,
                    "service": "plataforma-total-local",
                    "version": "5.1.0",
                    "mode": "local",
                    "runtime_mode": "local-first",
                    "stats": {
                        "courses": len(idx),
                        "free_courses": sum(1 for x in idx if x.get("free")),
                        "lessons": sum(int(x.get("l", 0)) for x in idx),
                    },
                    "connections": {
                        "curriculum": True,
                        "web_database": True,
                        "desktop_database": DESKTOP_DB.exists(),
                        "ollama": bool(os.environ.get("PT_OLLAMA_MODEL")) or self._ollama_available(),
                    },
                })

            if path == "/api/system":
                tools = {name: bool(shutil.which(name)) for name in ["git", "node", "docker", "ollama", "code"]}
                model = None
                try:
                    base = os.environ.get("PT_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
                    with urllib.request.urlopen(base + "/api/tags", timeout=1.5) as response:
                        models = json.loads(response.read().decode()).get("models") or []
                        model = models[0].get("name") if models else None
                except Exception:
                    pass
                return self.js({
                    "ok": True, "version": "5.1.0", "mode": "local-first",
                    "data_dir": str(APP_DIR), "web_db": str(DB), "desktop_db": str(DESKTOP_DB),
                    "tools": tools, "ollama": bool(model), "ollama_model": model,
                })

            if path == "/api/catalog":
                idx = load_catalog()
                return self.js({
                    "ok": True, "version": "5.1.0",
                    "stats": {
                        "courses": len(idx),
                        "free_courses": sum(1 for x in idx if x.get("free")),
                        "lessons": sum(int(x.get("l", 0)) for x in idx),
                    },
                    "data": idx,
                })

            if path == "/api/course":
                slug = (query.get("slug", [""])[0] or "").strip()
                if not re.fullmatch(r"[a-z0-9-]{3,80}", slug, re.I):
                    return self.js({"ok": False, "error": "slug inválido"}, 400)
                course = load_course(slug)
                return self.js({"ok": True, "data": course}) if course else self.js({"ok": False, "error": "curso no encontrado"}, 404)

            if path == "/api/search":
                q = " ".join(query.get("q", [""]))[:120]
                terms = set(tokens(q))
                results = []
                for i, name in enumerate(COURSE_NAMES):
                    score = len(terms & set(tokens(name)))
                    if score:
                        results.append({"ci": i, "s": course_slug(i, name), "n": name, "score": score})
                results.sort(key=lambda x: x["score"], reverse=True)
                return self.js({"ok": True, "data": results[:20]})

            if path == "/api/progreso":
                alias = self.auth() or "local"
                return self.js({"ok": True, "data": load_progress(alias)})

            if path == "/api/pro":
                alias = self.auth() or "local"
                conn = db()
                try:
                    row = conn.execute(
                        "SELECT p.estado FROM pro_alias pa JOIN pro p ON p.email=pa.email WHERE pa.alias=?",
                        (alias,),
                    ).fetchone()
                finally:
                    conn.close()
                active = bool(row and int(row[0]) == 1) or os.environ.get("PT_LOCAL_PRO") == "1"
                return self.js({"ok": True, "pro": active})

            if path == "/api/certificado":
                code = (query.get("codigo", [""])[0] or "").strip().upper()
                code = code if code.startswith("PT-") else "PT-" + code
                conn = db()
                try:
                    row = conn.execute("SELECT alias,curso,fecha FROM certificados WHERE codigo=?", (code,)).fetchone()
                finally:
                    conn.close()
                if row:
                    return self.js({"ok": True, "valido": True, "quien": str(row[0])[:3] + "***", "curso": row[1], "fecha": row[2]})
                conn = desktop_db()
                try:
                    raw = code.removeprefix("PT-")
                    row = conn.execute(
                        "SELECT alumno,curso,fecha FROM certificados WHERE codigo=? OR codigo=?",
                        (raw, code),
                    ).fetchone()
                finally:
                    conn.close()
                if row:
                    return self.js({"ok": True, "valido": True, "quien": str(row[0])[:3] + "***", "curso": row[1], "fecha": str(row[2])[:10]})
                return self.js({"ok": True, "valido": False})

            if path == "/api/projects":
                alias = self.auth() or "local"
                conn = db()
                try:
                    rows = conn.execute(
                        "SELECT id,name,path,created,updated FROM projects WHERE alias=? ORDER BY updated DESC",
                        (alias,),
                    ).fetchall()
                finally:
                    conn.close()
                return self.js({"ok": True, "projects": [dict(id=r[0], name=r[1], path=r[2], created=r[3], updated=r[4]) for r in rows]})

            return self.js({"ok": False, "error": "endpoint no encontrado"}, 404)

        return self.static(path)

    def _ollama_available(self):
        try:
            base = os.environ.get("PT_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
            with urllib.request.urlopen(base + "/api/tags", timeout=1.0) as response:
                return bool((json.loads(response.read().decode()).get("models") or []))
        except Exception:
            return False

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/api/auth":
            body = self.body()
            alias = str(body.get("alias", "")).strip().lower()
            pin = str(body.get("pin", ""))
            if not alias_ok(alias) or len(pin) < 4:
                return self.js({"ok": False, "error": "alias 3-24 y PIN 4+"}, 400)
            conn = db()
            try:
                row = conn.execute("SELECT hash,salt FROM users WHERE alias=?", (alias,)).fetchone()
                failed = conn.execute("SELECT n,ts FROM intentos WHERE alias=?", (alias,)).fetchone()
                if failed and failed[1] > now() and int(failed[0]) >= 5:
                    return self.js({"ok": False, "error": "demasiados intentos, esperá 10 min"}, 429)
                if row:
                    if not secrets.compare_digest(pbk(pin, row[1]), row[0]):
                        n = (int(failed[0]) if failed else 0) + 1
                        stamp = now()
                        conn.execute(
                            "INSERT INTO intentos(alias,n,ts) VALUES(?,?,?) "
                            "ON CONFLICT(alias) DO UPDATE SET n=?,ts=?",
                            (alias, n, stamp, n, stamp),
                        )
                        conn.commit()
                        return self.js({"ok": False, "error": "PIN incorrecto"}, 401)
                    conn.execute("DELETE FROM intentos WHERE alias=?", (alias,))
                else:
                    salt = secrets.token_hex(16)
                    conn.execute(
                        "INSERT INTO users(alias,hash,salt,creado) VALUES(?,?,?,?)",
                        (alias, pbk(pin, salt), salt, now()),
                    )
                token = secrets.token_hex(32)
                expira = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=30)).isoformat()
                conn.execute("INSERT INTO sessions(token,alias,expira) VALUES(?,?,?)", (token, alias, expira))
                conn.commit()
            finally:
                conn.close()
            state = load_progress(alias)
            save_progress(alias, state)
            return self.js({"ok": True, "alias": alias, "token": token, "data": state})

        alias = self.auth()

        if path == "/api/progreso":
            body = self.body()
            incoming = body.get("data") or {}
            if not isinstance(incoming, dict):
                return self.js({"ok": False, "error": "data inválida"}, 400)
            state = save_progress(alias or "local", incoming)
            return self.js({"ok": True, "data": state})

        if path in ("/api/pro", "/api/certificado") and not alias:
            return self.js({"ok": False, "error": "sesión inválida"}, 401)

        if path == "/api/pro":
            body = self.body()
            email = str(body.get("email", "")).strip().lower()
            allowed_emails = {x.strip().lower() for x in os.environ.get("PT_LOCAL_PRO_EMAILS", "").split(",") if x.strip()}
            allowed = os.environ.get("PT_LOCAL_PRO") == "1" or email in allowed_emails
            if not email and allowed:
                email = "local@localhost"
            conn = db()
            try:
                existing = conn.execute("SELECT estado FROM pro WHERE email=?", (email,)).fetchone() if email else None
                if not (allowed or (existing and int(existing[0]) == 1)):
                    return self.js({"ok": False, "pro": False, "error": "email sin PRO local"}, 404)
                stamp = now()
                conn.execute(
                    "INSERT INTO pro(email,estado,actualizado) VALUES(?,?,?) "
                    "ON CONFLICT(email) DO UPDATE SET estado=1,actualizado=excluded.actualizado",
                    (email, 1, stamp),
                )
                conn.execute(
                    "INSERT INTO pro_alias(alias,email,actualizado) VALUES(?,?,?) "
                    "ON CONFLICT(alias) DO UPDATE SET email=excluded.email,actualizado=excluded.actualizado",
                    (alias, email, stamp),
                )
                conn.commit()
            finally:
                conn.close()
            return self.js({"ok": True, "pro": True})

        if path == "/api/admin":
            body = self.body()
            if body.get("secret") != os.environ.get("PT_ADMIN_SECRET"):
                return self.js({"ok": False, "error": "no autorizado"}, 401)
            email = str(body.get("email", "")).strip().lower()
            state = 0 if str(body.get("accion", "pro")) == "quitar" else 1
            conn = db()
            try:
                stamp = now()
                conn.execute(
                    "INSERT INTO pro(email,estado,evento,actualizado) VALUES(?,?,?,?) "
                    "ON CONFLICT(email) DO UPDATE SET estado=excluded.estado,evento=excluded.evento,actualizado=excluded.actualizado",
                    (email, state, "local_admin", stamp),
                )
                conn.commit()
            finally:
                conn.close()
            return self.js({"ok": True, "estado": state, "email": email})

        if path == "/api/certificado":
            body = self.body()
            code = str(body.get("codigo", "")).strip().upper()
            code = code if code.startswith("PT-") else "PT-" + code
            course = str(body.get("curso", "")).strip()
            if not re.fullmatch(r"PT-[A-Z0-9-]{3,24}", code) or not course:
                return self.js({"ok": False, "error": "certificado inválido"}, 400)
            conn = db()
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO certificados(codigo,alias,curso,fecha) VALUES(?,?,?,?)",
                    (code, alias, course, dt.date.today().isoformat()),
                )
                conn.commit()
            finally:
                conn.close()
            state = load_progress(alias)
            certs = [x for x in state.get("certs", []) if x.get("codigo") != code]
            certs.append({"codigo": code, "curso": course, "fecha": dt.date.today().isoformat()})
            state["certs"] = certs[-100:]
            save_progress(alias, state)
            return self.js({"ok": True, "codigo": code})

        if path == "/api/chat":
            body = self.body()
            messages = body.get("messages") or []
            reply = ollama(messages)
            if reply:
                return self.js({"ok": True, "respuesta": reply, "backend": "ollama"})
            last = next((m.get("content", "") for m in reversed(messages) if m.get("role") == "user"), "")
            return self.js({"ok": True, "respuesta": local_tutor(last), "backend": "local-rag"})

        if path == "/api/projects":
            alias = alias or "local"
            body = self.body()
            name = str(body.get("name", "")).strip() or "Proyecto sin nombre"
            safe = re.sub(r"[^a-zA-Z0-9 _.-]+", "", name).strip()[:60] or "proyecto"
            pid = secrets.token_hex(8)
            project_path = PROJECTS_DIR / f"{pid}-{slugify(safe)[:40]}"
            project_path.mkdir(parents=True, exist_ok=True)
            (project_path / "README.md").write_text(
                f"# {name}\\n\\nProyecto creado desde Plataforma Total.\\n",
                encoding="utf-8",
            )
            stamp = now()
            conn = db()
            try:
                conn.execute(
                    "INSERT INTO projects(id,alias,name,path,created,updated) VALUES(?,?,?,?,?,?)",
                    (pid, alias, name, str(project_path), stamp, stamp),
                )
                conn.commit()
            finally:
                conn.close()
            return self.js({
                "ok": True,
                "project": {"id": pid, "name": name, "path": str(project_path), "created": stamp, "updated": stamp},
            }, 201)

        return self.js({"ok": False, "error": "endpoint no encontrado"}, 404)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/projects":
            return self.js({"ok": False, "error": "endpoint no encontrado"}, 404)
        alias = self.auth() or "local"
        pid = parse_qs(parsed.query).get("id", [""])[0]
        conn = db()
        try:
            row = conn.execute("SELECT alias,path FROM projects WHERE id=?", (pid,)).fetchone()
            if not row or row[0] != alias:
                return self.js({"ok": False, "error": "proyecto no encontrado"}, 404)
            conn.execute("DELETE FROM projects WHERE id=?", (pid,))
            conn.commit()
            try:
                shutil.rmtree(row[1])
            except Exception:
                pass
        finally:
            conn.close()
        return self.js({"ok": True})

    def static(self, path):
        rel = path.lstrip("/") or "index.html"
        candidates = [DIST / rel, DIST / rel / "index.html"]
        target = next((p for p in candidates if p.is_file()), None)
        if target is None:
            return self.send_error(404, "Archivo no encontrado")
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(str(target))[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

def load_progress(alias: str) -> dict:
    conn = db()
    try:
        row = conn.execute("SELECT data FROM progreso WHERE alias=?", (alias,)).fetchone()
        current = json.loads(row[0]) if row else {}
    finally:
        conn.close()
    return merge_state(current, desktop_snapshot())

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("PT_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PT_PORT", "8787")))
    args = parser.parse_args()
    if not DIST.exists():
        raise SystemExit("Falta web/dist. Ejecutá npm run build:local dentro de web.")
    db().close()
    desktop_db().close()
    print(f"Plataforma Total v5.1 → http://{args.host}:{args.port}")
    print(f"Currículo: {len(COURSE_NAMES)} cursos · {sum(len(v) for v in CURSOS.values())} lecciones")
    print(f"Datos: {APP_DIR}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()

if __name__ == "__main__":
    main()
