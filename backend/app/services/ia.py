import logging
import httpx
from app.config import settings

MOCK = {"respuesta": None, "llamadas": 0}
_cache_modelos = {"ts": 0, "lista": []}

SYSTEM = """Eres el asistente administrativo de la consulta de psicología "{nombre}". Solo respondes sobre: cómo reservar, modalidades (online/presencial), duración y tarifas, primera sesión, política de cancelación, horarios disponibles.
No das consejo psicológico, no diagnosticas ni opinas sobre síntomas: si te preguntan algo clínico, di que eso se trata en sesión y ofrece reservar.
No pidas ni repitas datos personales. Español, máximo 4 frases, tono cercano. Si procede reservar, termina con la etiqueta exacta [ABRIR_AGENDA].
Datos: modalidades {modalidades}; sesiones {tipos}; dirección presencial {direccion}; cancelación: {politica}.
Próximos huecos online: {huecos_online}. Próximos huecos presenciales: {huecos_presencial}."""

async def modelos_gratis() -> list[str]:
    import time
    if settings.OPENROUTER_MODELOS:
        return [m.strip() for m in settings.OPENROUTER_MODELOS.split(",") if m.strip()]
    if time.time() - _cache_modelos["ts"] < 3600 and _cache_modelos["lista"]:
        return _cache_modelos["lista"]
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.get("https://openrouter.ai/api/v1/models")
            if r.status_code == 200:
                modelos = [m["id"] for m in r.json().get("data", []) if m["id"].endswith(":free")][:5]
                _cache_modelos["ts"] = time.time()
                _cache_modelos["lista"] = modelos
                return modelos
    except Exception:
        logging.warning("No se pudieron listar modelos de OpenRouter")
    return []

async def responder_ia(mensajes: list[dict], contexto: dict) -> str | None:
    if settings.modo_test:
        MOCK["llamadas"] += 1
        return MOCK["respuesta"]
    if not settings.OPENROUTER_API_KEY:
        return None
    cuerpo_sys = SYSTEM.format(**contexto)
    async with httpx.AsyncClient(timeout=20) as c:
        for modelo in await modelos_gratis():
            try:
                r = await c.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                        "HTTP-Referer": settings.FRONTEND_URL,
                        "X-Title": "Tu Espacio"
                    },
                    json={
                        "model": modelo,
                        "messages": [{"role": "system", "content": cuerpo_sys}, *mensajes],
                        "max_tokens": 300,
                        "temperature": 0.3
                    }
                )
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
                logging.warning("OpenRouter %s → %s", modelo, r.status_code)
            except httpx.HTTPError as e:
                logging.warning("OpenRouter %s error %s", modelo, e)
    return None

def responder_reglas(texto: str) -> tuple[str, list[str]]:
    t = texto.lower()
    if any(w in t for w in ["reserv", "cita", "agenda", "horario", "disponib"]):
        return ("Pulsa el botón de reservar para ver los huecos disponibles. ¿Qué modalidad prefieres?", ["abrir_agenda"])
    if any(w in t for w in ["precio", "tarifa", "cuesta", "coste", "pago"]):
        return ("Las tarifas se muestran al reservar. Cada tipo de sesión tiene su precio indicado.", ["abrir_agenda"])
    if any(w in t for w in ["online", "videollamada", "distancia"]):
        return ("La modalidad online se realiza por videollamada desde un lugar privado para ti.", [])
    if any(w in t for w in ["presencial", "direccion", "ubicacion", "donde"]):
        return ("La consulta presencial tiene dirección en los ajustes. Consulta la sección de sesiones.", [])
    if any(w in t for w in ["cancel", "cambiar", "reprogram"]):
        return ("Puedes cancelar o reagendar desde el enlace que recibiste por email. También puedes gestionarlo desde la web.", [])
    if any(w in t for w in ["primera", "empezar", "funciona"]):
        return ("La primera sesión sirve para explorar qué necesitas y valorar cómo trabajar juntos. No necesitas llegar preparado.", ["abrir_agenda"])
    if any(w in t for w in ["duracion", "dura", "minutos", "frecuencia"]):
        return ("Las sesiones duran 50 minutos. La frecuencia se acuerda según tus necesidades.", [])
    return ("Puedo ayudarte con dudas sobre reservas, modalidades y tarifas. ¿Quieres abrir la agenda?", ["abrir_agenda"])

async def estado_openrouter() -> dict:
    if settings.modo_test:
        return {"is_free_tier": True, "limit_remaining": 0, "usage": 0, "modelos": []}
    if not settings.OPENROUTER_API_KEY:
        return {"error": "Sin OPENROUTER_API_KEY configurada"}
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.get(
                "https://openrouter.ai/api/v1/key",
                headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"}
            )
            if r.status_code == 200:
                data = r.json().get("data", {})
                return {
                    "is_free_tier": data.get("is_free_tier", True),
                    "limit_remaining": data.get("limit_remaining", 0),
                    "usage": data.get("usage", 0),
                    "modelos": await modelos_gratis()
                }
            return {"error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}
