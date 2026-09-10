from checks import *
FICHEROS = ["DECISIONES.md", "CHECKLIST_CLIENTE.md", ".gitignore", "GUIA_MAESTRA.md",
            "backend/requirements.txt", "backend/.env.example", "backend/.env", "backend/pytest.ini",
            "backend/app/__init__.py", "backend/app/main.py", "backend/app/config.py", "backend/app/db.py",
            "backend/app/services/__init__.py", "backend/app/routers/__init__.py", "backend/tests/__init__.py",
            "frontend/package.json", "frontend/.env.example", "frontend/vercel.json", "frontend/src/App.tsx",
            "HARNESS/PROMPT_SESION.md", "HARNESS/STATE.md"] + [f"HARNESS/checks/fase{i}.py" for i in range(7)] \
           + [f"HARNESS/MANUAL_0{i}.md" for i in range(7)]

def salud():
    with cliente() as c:
        r = c.get("/api/salud"); return (r.status_code == 200 and r.json().get("ok") is True, r.text)

def mongo_ping():
    async def go():
        from app.db import get_cliente
        return await get_cliente().admin.command("ping")
    res = corre(go()); return (res.get("ok") == 1, str(res))

def env_relleno():
    faltan = [k for k in ("MONGO_URI", "ADMIN_PASSWORD", "JWT_SECRET", "CRON_SECRET") if not leer_env(k) or "cambiame" in leer_env(k)]
    return (not faltan, "rellena en backend/.env: " + ", ".join(faltan))

CRITERIOS = [existe(f) for f in FICHEROS] + [
    contiene(".gitignore", ".env"), contiene("frontend/package.json", "react-router-dom"),
    contiene("frontend/vercel.json", "index.html"), contiene("backend/pytest.ini", "asyncio_mode = auto"),
    ("backend/.env con secretos reales (sin 'cambiame')", env_relleno),
    ("GET /api/salud → 200 {ok:true}", salud), ("MongoDB ping", mongo_ping),
]