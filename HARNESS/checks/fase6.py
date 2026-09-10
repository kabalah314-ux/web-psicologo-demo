from checks import *
import httpx

def _api(): return leer_env("API_URL_PROD").rstrip("/")
def _front(): return leer_env("FRONTEND_URL").rstrip("/")

def prod_salud():
    r = httpx.get(f"{_api()}/api/salud", timeout=90); return (r.status_code == 200 and r.json().get("ok") is True, r.text[:200])
def prod_config():
    r = httpx.get(f"{_api()}/api/publico/config", timeout=60); return (r.status_code == 200 and "tipos_sesion" in r.json(), r.text[:200])
def prod_tareas_401():
    r = httpx.post(f"{_api()}/api/tareas/recordatorios", timeout=60); return (r.status_code == 401, f"{r.status_code}")
def prod_tareas_ok():
    r = httpx.post(f"{_api()}/api/tareas/recordatorios", headers={"X-Cron-Secret": leer_env("CRON_SECRET")}, timeout=60)
    return (r.status_code == 200 and "enviados" in r.json(), r.text[:200])
def prod_front():
    r = httpx.get(_front(), timeout=60, follow_redirects=True); return (r.status_code == 200 and "<div id=\"root\"" in r.text, f"{r.status_code}")
def prod_front_ruta_profunda():
    r = httpx.get(f"{_front()}/gestionar/token-inexistente", timeout=60, follow_redirects=True); return (r.status_code == 200, f"{r.status_code} (¿falta vercel.json?)")
def prod_cors():
    r = httpx.options(f"{_api()}/api/publico/config", headers={"Origin": _front(), "Access-Control-Request-Method": "GET"}, timeout=60)
    return (r.headers.get("access-control-allow-origin") in (_front(), "*"), f"allow-origin={r.headers.get('access-control-allow-origin')}")
def checklist():
    t = (RAIZ / "CHECKLIST_CLIENTE.md").read_text(encoding="utf-8"); n = t.count("- [ ]"); return (n >= 15, f"{n} casillas")
def env_prod():
    faltan = [k for k in ("API_URL_PROD", "FRONTEND_URL") if not leer_env(k).startswith("https://")]
    return (not faltan, "en backend/.env deben ser https://…: " + ", ".join(faltan))

CRITERIOS = [("API_URL_PROD y FRONTEND_URL definidos (https)", env_prod),
             ("prod GET /api/salud", prod_salud), ("prod GET /api/publico/config", prod_config),
             ("prod tareas sin secreto → 401", prod_tareas_401), ("prod tareas con secreto → 200", prod_tareas_ok),
             ("prod frontend 200", prod_front), ("prod ruta profunda /gestionar/x → 200 (rewrite)", prod_front_ruta_profunda),
             ("prod CORS permite el frontend", prod_cors),
             ("CHECKLIST_CLIENTE.md ≥ 15 casillas", checklist)]