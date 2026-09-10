import pathlib, subprocess, sys, os, re, asyncio
RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
CON_RED = os.environ.get("HARNESS_CON_RED") == "1"

def existe(rel):
    def f(): return ((RAIZ / rel).exists(), f"falta {rel}")
    return (f"existe {rel}", f)

def contiene(rel, texto):
    def f():
        p = RAIZ / rel
        if not p.exists(): return False, f"falta {rel}"
        return (texto in p.read_text(encoding="utf-8", errors="ignore"), f"{rel} no contiene '{texto}'")
    return (f"{rel} contiene '{texto}'", f)

def no_contiene_en_dir(rel_dir, texto, ext=(".ts", ".tsx", ".css", ".html")):
    def f():
        for p in (RAIZ / rel_dir).rglob("*"):
            if p.is_file() and p.suffix in ext and "node_modules" not in p.parts \
               and texto in p.read_text(encoding="utf-8", errors="ignore"):
                return False, f"'{texto}' sigue en {p.relative_to(RAIZ)}"
        return True, ""
    return (f"'{texto}' eliminado de {rel_dir}", f)

def pytest_pasa(*ficheros, minimo=1):
    def f():
        env = {**os.environ, "MODO_TEST": "true", "MONGO_DB": "tuespacio_test"}
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *ficheros],
                           cwd=RAIZ / "backend", capture_output=True, text=True, env=env)
        salida = r.stdout + r.stderr
        m = re.search(r"(\d+) passed", salida); n = int(m.group(1)) if m else 0
        return (r.returncode == 0 and n >= minimo, f"{n} passed (mínimo {minimo})\n" + salida[-1500:])
    return (f"pytest {' '.join(ficheros)} (≥{minimo} tests, todos PASS)", f)

def comando_ok(cmd, cwd):
    def f():
        r = subprocess.run(cmd, cwd=RAIZ / cwd, shell=True, capture_output=True, text=True)
        return (r.returncode == 0, (r.stdout + r.stderr)[-1500:])
    return (f"`{cmd}` en {cwd}", f)

def cliente():
    """TestClient síncrono de la app en MODO_TEST (ejecuta el lifespan)."""
    os.environ["MODO_TEST"] = "true"; os.environ["MONGO_DB"] = "tuespacio_test"
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)

def rutas_openapi():
    with cliente() as c:
        paths = c.app.openapi()["paths"]
    return {(m.upper(), p) for p, ms in paths.items() for m in ms}

def rutas_existen(esperadas):
    def f():
        tienen = rutas_openapi(); faltan = [f"{m} {p}" for m, p in esperadas if (m, p) not in tienen]
        return (not faltan, "faltan: " + ", ".join(faltan))
    return (f"{len(esperadas)} rutas definidas en la API", f)

def corre(coro):
    """Ejecuta una corrutina con el cliente Motor limpio antes y después."""
    from app import db
    db.cerrar()
    try: return asyncio.run(coro)
    finally: db.cerrar()

def leer_env(clave, default=""):
    p = RAIZ / "backend" / ".env"
    if not p.exists(): return default
    m = re.search(rf"^{clave}=(.*)$", p.read_text(encoding="utf-8"), re.M)
    return m.group(1).strip() if m else default

def solo_con_red(nombre, fn):
    def f():
        if not CON_RED: return True, "omitido (sin --con-red)"
        return fn()
    return (nombre + " [red]", f)