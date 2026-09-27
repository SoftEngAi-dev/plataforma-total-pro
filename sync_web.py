"""
☁️ sync_web.py — Cliente de nube OPCIONAL para Plataforma Total (app escritorio).
Conecta con el backend cloud usando el mismo contrato unificado que la web (pt_web_v3). Solo stdlib (urllib): no agrega dependencias.

Funciones:
  login(alias, pin)        → (ok, {alias, token} | {error})
  pull(token)              → dict datos nube | None
  push(token, data)        → True/False
  es_pro(token)            → bool (PRO comprado vía web/Lemon Squeezy)
  cert_registrar(token, codigo, curso) → True/False  (certificado verificable online)
"""
import json
import os
import urllib.request
import urllib.error
import time

API = os.environ.get("PT_CLOUD_API", "https://plataforma-total-web.pages.dev/api/")
if not API.endswith("/"):
    API += "/"
TIMEOUT = 20


def _req(path, payload=None, token=None):
    """Llamada JSON simple. Devuelve (status, dict) o (status, {'error': msg})."""
    req = urllib.request.Request(API + path)
    # Cloudflare WAF bloquea el UA por defecto de Python-urllib → UA neutro de app
    req.add_header("User-Agent", "PlataformaTotal-Desktop/5.0 (+python-urllib)")
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("X-Token", token)
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, data=data, timeout=TIMEOUT) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode("utf-8"))
            except Exception:
                return e.code, {"error": f"HTTP {e.code}"}
        except Exception as e:
            if attempt == 0:
                time.sleep(0.8)
                continue
            return 0, {"error": f"sin conexión ({type(e).__name__})"}



def health():
    st, d = _req("health")
    return st == 200 and d.get("ok"), d


def login(alias, pin):
    """alias+PIN (3-24 / 4+). Devuelve (True, datos) o (False, {'error': ...})."""
    st, d = _req("auth", {"alias": alias, "pin": pin})
    if st == 200 and d.get("ok"):
        return True, d
    return False, d


def pull(token):
    st, d = _req("progreso", token=token)
    if st == 200 and d.get("ok"):
        return d.get("data") or {}
    return None


def push(token, data):
    st, d = _req("progreso", {"data": data}, token=token)
    return st == 200 and bool(d.get("ok"))


def es_pro(token):
    st, d = _req("pro", token=token)
    return st == 200 and bool(d.get("pro"))


def cert_registrar(token, codigo, curso):
    st, d = _req("certificado", {"codigo": codigo, "curso": curso}, token=token)
    return st == 200 and bool(d.get("ok"))
