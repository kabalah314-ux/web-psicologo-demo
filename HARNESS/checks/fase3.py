from checks import *
RUTAS = [("POST", "/api/admin/login"), ("GET", "/api/admin/citas"), ("PATCH", "/api/admin/citas/{id}"),
         ("GET", "/api/admin/disponibilidad"), ("PUT", "/api/admin/disponibilidad"),
         ("GET", "/api/admin/bloqueos"), ("POST", "/api/admin/bloqueos"), ("DELETE", "/api/admin/bloqueos/{id}"),
         ("GET", "/api/admin/ajustes"), ("PUT", "/api/admin/ajustes"), ("POST", "/api/admin/telegram/test"),
         ("GET", "/api/admin/ia/estado"),
         ("POST", "/api/tareas/recordatorios"), ("POST", "/api/tareas/resumen-diario"), ("POST", "/api/tareas/purga")]

def todo_admin_401_sin_token():
    malos = []
    with cliente() as c:
        for m, p in rutas_openapi():
            if p.startswith("/api/admin/") and p != "/api/admin/login" or p.startswith("/api/tareas/"):
                r = c.request(m, p.replace("{id}", "000000000000000000000000"), json={})
                if r.status_code != 401: malos.append(f"{m} {p} → {r.status_code}")
    return (not malos, "; ".join(malos))

def ajustes_invalidos_422():
    with cliente() as c:
        r = c.post("/api/admin/login", json={"usuario": leer_env("ADMIN_USUARIO", "admin"), "password": leer_env("ADMIN_PASSWORD")})
        if r.status_code != 200: return False, f"login → {r.status_code} {r.text}"
        h = {"Authorization": f"Bearer {r.json()['token']}"}
        a = c.get("/api/admin/ajustes", headers=h).json(); a["plazo_cancelacion_horas"] = -1
        r2 = c.put("/api/admin/ajustes", json=a, headers=h)
        r3 = c.get("/api/admin/ia/estado", headers=h)
        return (r2.status_code == 422 and r3.status_code == 200 and "is_free_tier" in r3.json(), f"put={r2.status_code} estado={r3.status_code}")

CRITERIOS = [existe("backend/app/services/security.py"), existe("backend/app/routers/admin.py"),
             existe("backend/app/routers/tareas.py"), existe("backend/tests/test_admin.py"),
             contiene("backend/app/services/security.py", "auto_error=False"),
             rutas_existen(RUTAS),
             ("todas las rutas admin (salvo login) y tareas → 401 sin token", todo_admin_401_sin_token),
             ("PUT /ajustes inválido → 422 y GET /ia/estado → 200", ajustes_invalidos_422),
             pytest_pasa("tests/test_admin.py", minimo=9)]