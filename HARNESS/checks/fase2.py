from checks import *
RUTAS = [("GET", "/api/publico/config"), ("GET", "/api/publico/huecos"), ("POST", "/api/publico/citas"),
         ("GET", "/api/publico/citas/{token}"), ("POST", "/api/publico/citas/{token}/cancelar"),
         ("POST", "/api/publico/citas/{token}/reagendar"), ("GET", "/api/publico/citas/{token}/ics"),
         ("POST", "/api/publico/contacto-urgente")]

def honeypot_y_validacion():
    with cliente() as c:
        r1 = c.post("/api/publico/citas", json={"inicio": "2030-01-06T08:00:00Z", "modalidad": "online", "tipo_sesion": "primera",
                                                 "nombre": "Bot", "email": "a@b.com", "consentimiento": True, "website": "spam"})
        r2 = c.post("/api/publico/citas", json={"inicio": "2030-01-06T08:00:00Z", "modalidad": "online", "tipo_sesion": "primera",
                                                 "nombre": "Ana", "email": "a@b.com", "consentimiento": False, "website": ""})
        r3 = c.get("/api/publico/huecos", params={"modalidad": "online", "desde": "2030-01-06", "dias": 31})
        return (r1.status_code == 400 and r2.status_code == 422 and r3.status_code == 422, f"{r1.status_code} {r2.status_code} {r3.status_code}")

def telegram_real():
    async def go():
        os.environ["MODO_TEST"] = "false"
        from app.services.notify import telegram_enviar
        return await telegram_enviar("✅ Arnés Tu Espacio: prueba de Telegram (fase 2)")
    if not leer_env("TELEGRAM_BOT_TOKEN"): return True, "omitido: sin TELEGRAM_BOT_TOKEN"
    return (corre(go()), "telegram_enviar devolvió False")

CRITERIOS = [existe("backend/app/schemas.py"), existe("backend/app/services/notify.py"), existe("backend/app/services/citas.py"),
             existe("backend/app/routers/publico.py"), existe("backend/tests/conftest.py"), existe("backend/tests/test_citas.py"),
             contiene("backend/app/services/citas.py", "DuplicateKeyError"),
             contiene("backend/tests/test_citas.py", "gather"),
             rutas_existen(RUTAS),
             ("honeypot 400, consentimiento false 422, dias>30 422", honeypot_y_validacion),
             pytest_pasa("tests/test_citas.py", minimo=12),
             solo_con_red("Telegram real al psicólogo", telegram_real)]