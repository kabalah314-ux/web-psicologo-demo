from checks import *
import json

def crisis_sin_ia():
    with cliente() as c:
        from app.services import ia
        ia.MOCK.update(respuesta="NO DEBERÍA LLEGAR", llamadas=0)
        r = c.post("/api/chat", json={"mensajes": [{"rol": "usuario", "contenido": "ya no puedo más, me quiero morir"}]})
        d = r.json()
        return (r.status_code == 200 and d.get("tipo") == "crisis" and "emergencias" in d.get("acciones", [])
                and "024" in d.get("respuesta", "") and ia.MOCK["llamadas"] == 0, r.text)

def etiqueta_agenda():
    with cliente() as c:
        from app.services import ia
        ia.MOCK.update(respuesta="Claro, elige la hora que prefieras. [ABRIR_AGENDA]", llamadas=0)
        r = c.post("/api/chat", json={"mensajes": [{"rol": "usuario", "contenido": "quiero reservar"}]}); d = r.json()
        return (d.get("tipo") == "ia" and "[ABRIR_AGENDA]" not in d.get("respuesta", "") and "abrir_agenda" in d.get("acciones", []), r.text)

def ia_real():
    import httpx
    if not leer_env("OPENROUTER_API_KEY"): return False, "falta OPENROUTER_API_KEY"
    os.environ["MODO_TEST"] = "false"
    with cliente() as c:
        r = c.post("/api/chat", json={"mensajes": [{"rol": "usuario", "contenido": "¿Cuánto dura una sesión?"}]}); d = r.json()
    return (r.status_code == 200 and d.get("tipo") in ("ia", "reglas") and 0 < len(d.get("respuesta", "")) < 800,
            f"tipo={d.get('tipo')} (si es 'reglas', revisa cupo/modelos con GET /api/admin/ia/estado) {r.text[:300]}")

CRITERIOS = [existe("backend/app/services/ia.py"), existe("backend/app/routers/chat.py"), existe("backend/tests/test_ia.py"),
             contiene("backend/app/services/ia.py", "openrouter.ai/api/v1/chat/completions"),
             contiene("backend/app/services/ia.py", "openrouter.ai/api/v1/key"),
             contiene("backend/app/routers/chat.py", "detectar_crisis"),
             rutas_existen([("POST", "/api/chat")]),
             ("crisis → tipo crisis, 024, y la IA NO se llama", crisis_sin_ia),
             ("[ABRIR_AGENDA] se convierte en acción", etiqueta_agenda),
             pytest_pasa("tests/test_ia.py", minimo=5),
             solo_con_red("petición real a OpenRouter (gasta 1 del cupo)", ia_real)]