import secrets, logging
from datetime import datetime, timedelta, timezone
from pymongo.errors import DuplicateKeyError
from app import db
from app.config import settings
from app.services.agenda import calcular_huecos, solapa
from app.services.video import enlace_video
from app.services.notify import telegram_enviar, email_enviar
from app.services.ics import generar_ics

def _html_confirmacion(cita, ajustes):
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(ajustes["zona_horaria"])
    fecha_local = cita["inicio"].astimezone(tz).strftime("%A %d/%m/%Y %H:%M")
    gestion_url = f"{settings.FRONTEND_URL}/gestionar/{cita['token']}"
    video = cita.get("video_enlace", "")
    politica = ajustes.get("textos", {}).get("politica_cancelacion", "")
    html = f"""<h2>Tu cita está confirmada</h2>
<p><strong>Fecha:</strong> {fecha_local}</p>
<p><strong>Modalidad:</strong> {cita['modalidad']}</p>
<p><strong>Duración:</strong> {ajustes['duracion_min']} minutos</p>
"""
    if video:
        html += f'<p><strong>Vídeo:</strong> <a href="{video}">{video}</a></p>'
    html += f"""
<p><strong>Gestionar tu cita:</strong> <a href="{gestion_url}">{gestion_url}</a></p>
<p>{politica}</p>
"""
    return html

def _html_cancelacion(cita, ajustes):
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(ajustes["zona_horaria"])
    fecha_local = cita["inicio"].astimezone(tz).strftime("%A %d/%m/%Y %H:%M")
    return f"""<h2>Tu cita ha sido cancelada</h2>
<p><strong>Fecha original:</strong> {fecha_local}</p>
<p>Si quieres reservar de nuevo, visita nuestra web.</p>"""

def _html_reagendada(cita, ajustes):
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(ajustes["zona_horaria"])
    fecha_local = cita["inicio"].astimezone(tz).strftime("%A %d/%m/%Y %H:%M")
    gestion_url = f"{settings.FRONTEND_URL}/gestionar/{cita['token']}"
    return f"""<h2>Tu cita ha sido cambiada</h2>
<p><strong>Nueva fecha:</strong> {fecha_local}</p>
<p><strong>Gestionar tu cita:</strong> <a href="{gestion_url}">{gestion_url}</a></p>"""

def _html_recordatorio(cita, ajustes):
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(ajustes["zona_horaria"])
    fecha_local = cita["inicio"].astimezone(tz).strftime("%A %d/%m/%Y %H:%M")
    video = cita.get("video_enlace", "")
    gestion_url = f"{settings.FRONTEND_URL}/gestionar/{cita['token']}"
    html = f"""<h2>Recordatorio de tu cita</h2>
<p>Tu sesión es mañana.</p>
<p><strong>Fecha:</strong> {fecha_local}</p>
<p><strong>Modalidad:</strong> {cita['modalidad']}</p>
"""
    if video:
        html += f'<p><strong>Vídeo:</strong> <a href="{video}">{video}</a></p>'
    html += f'<p><strong>Gestionar:</strong> <a href="{gestion_url}">{gestion_url}</a></p>'
    return html

async def crear_cita(datos: dict, ajustes: dict, reglas: list, ahora_utc: datetime) -> dict:
    if datos.get("website"):
        raise ValueError("honeypot")

    inicio = datos["inicio"].astimezone(timezone.utc) if datos["inicio"].tzinfo else datos["inicio"].replace(tzinfo=timezone.utc)
    dia_local = datos["inicio"].astimezone(
        __import__("zoneinfo").ZoneInfo(ajustes["zona_horaria"])
    ).date() if datos["inicio"].tzinfo else datos["inicio"].date()

    db_c = db.get_db()
    bloqueos = await db_c["bloqueos"].find({"inicio": {"$lte": inicio}, "fin": {"$gt": inicio}}).to_list(100)
    citas_activas = await db_c["citas"].find({"estado": "activa", "inicio": {"$lte": inicio}, "fin": {"$gt": inicio}}).to_list(100)

    if bloqueos or citas_activas:
        raise ValueError("no_disponible")

    huecos = await _obtener_huecos(dia_local, datos["modalidad"], ajustes, reglas, ahora_utc)
    hueco_valido = any(h["inicio"] == inicio for h in huecos)

    if not hueco_valido:
        raise ValueError("no_disponible")

    tipo = next((t for t in ajustes["tipos_sesion"] if t["id"] == datos["tipo_sesion"]), None)
    duracion = timedelta(minutes=tipo["duracion_min"]) if tipo else timedelta(minutes=ajustes["duracion_min"])
    fin = inicio + duracion
    token = secrets.token_urlsafe(32)
    video = enlace_video(ajustes, token) if datos["modalidad"] == "online" else ""
    gestion_url = f"{settings.FRONTEND_URL}/gestionar/{token}"

    cita = {
        "inicio": inicio,
        "fin": fin,
        "modalidad": datos["modalidad"],
        "tipo_sesion": datos["tipo_sesion"],
        "nombre": datos["nombre"],
        "email": datos["email"],
        "telefono": datos.get("telefono", ""),
        "estado": "activa",
        "token": token,
        "video_enlace": video,
        "creado_en": ahora_utc,
        "cancelado_en": None,
        "cancelado_por": None,
        "recordatorio_enviado": False,
        "gestion_url": gestion_url,
    }

    try:
        await db_c["citas"].insert_one(cita)
    except DuplicateKeyError:
        raise ValueError("ocupado")

    html = _html_confirmacion(cita, ajustes)
    ics = generar_ics(cita, ajustes)
    await email_enviar(cita["email"], "Tu cita en Tu Espacio", html, ics)
    telegram_msg = f"🆕 Nueva cita: {cita['nombre']} ({cita['email']}) — {cita['modalidad']}"
    await telegram_enviar(telegram_msg)

    return {
        "id": str(cita.get("_id", token)),
        "inicio": inicio.isoformat().replace("+00:00", "Z"),
        "inicio_local": datos["inicio"].strftime("%Y-%m-%dT%H:%M") if datos["inicio"].tzinfo else inicio.strftime("%Y-%m-%dT%H:%M"),
        "modalidad": cita["modalidad"],
        "gestion_url": gestion_url,
        "video_enlace": video,
    }

async def _obtener_huecos(dia, modalidad, ajustes, reglas, ahora_utc):
    db_c = db.get_db()
    bloqueos = await db_c["bloqueos"].find({}).to_list(100)
    citas = await db_c["citas"].find({"estado": "activa"}).to_list(100)
    return calcular_huecos(dia, modalidad, ajustes, reglas, bloqueos, citas, ahora_utc)

async def cancelar_por_paciente(token: str, ajustes: dict, ahora_utc: datetime) -> dict:
    db_c = db.get_db()
    cita = await db_c["citas"].find_one({"token": token, "estado": "activa"})
    if not cita:
        raise ValueError("no_encontrada")

    desde = cita["inicio"] - ahora_utc
    plazo = timedelta(hours=ajustes["plazo_cancelacion_horas"])
    if desde < plazo:
        tz = __import__("zoneinfo").ZoneInfo(ajustes["zona_horaria"])
        fecha_local = cita["inicio"].astimezone(tz).strftime("%d/%m/%Y %H:%M")
        await telegram_enviar(f"⚠️ Solicitud de cancelación fuera de plazo: {cita['nombre']} {fecha_local}")
        raise ValueError("fuera_plazo")

    await db_c["citas"].update_one(
        {"token": token},
        {"$set": {"estado": "cancelada", "cancelado_en": ahora_utc, "cancelado_por": "paciente"}}
    )

    html = _html_cancelacion(cita, ajustes)
    await email_enviar(cita["email"], "Cita cancelada — Tu Espacio", html)

    return {"ok": True}
