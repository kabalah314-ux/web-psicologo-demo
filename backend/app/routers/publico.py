from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings
from app import db
from app.schemas import CitaEntrada, ReagendarEntrada, ContactoUrgente
from app.services.agenda import calcular_huecos
from app.services.citas import crear_cita, cancelar_por_paciente
from app.services.ics import generar_ics
from app.services.notify import telegram_enviar
from app.services.crisis import en_horario_laboral

router = APIRouter(prefix="/api/publico", tags=["publico"])
limiter = Limiter(key_func=get_remote_address)

@router.get("/config")
async def config():
    ajustes = await db.get_db()["ajustes"].find_one({"_id": "ajustes"})
    return {
        "nombre_profesional": ajustes["nombre_profesional"],
        "tipos_sesion": ajustes["tipos_sesion"],
        "modalidades": ajustes["modalidades"],
        "plazo_cancelacion_horas": ajustes["plazo_cancelacion_horas"],
        "direccion_presencial": ajustes["direccion_presencial"],
        "textos": ajustes["textos"],
        "zona_horaria": ajustes["zona_horaria"],
    }

@router.get("/huecos")
@limiter.limit("30/hour")
async def huecos(request: Request, modalidad: str, desde: str, dias: int = 14):
    if modalidad not in ("online", "presencial"):
        raise HTTPException(422, "Modalidad inválida")
    if dias > 30:
        raise HTTPException(422, "Máximo 30 días")

    db_c = db.get_db()
    ajustes = await db_c["ajustes"].find_one({"_id": "ajustes"})
    reglas = await db_c["disponibilidad"].find({}).to_list(100)
    bloqueos = await db_c["bloqueos"].find({}).to_list(100)
    citas = await db_c["citas"].find({"estado": "activa"}).to_list(100)

    desde_date = datetime.strptime(desde, "%Y-%m-%d").date()
    ahora_utc = datetime.now(timezone.utc)
    todos_huecos = []

    from datetime import timedelta as td
    for i in range(dias):
        dia = desde_date + td(days=i)
        huecos_dia = calcular_huecos(dia, modalidad, ajustes, reglas, bloqueos, citas, ahora_utc)
        todos_huecos.extend(huecos_dia)

    return {"huecos": [
        {"inicio": h["inicio"].isoformat().replace("+00:00", "Z"), "inicio_local": h["inicio_local"], "fin": h["fin"].isoformat().replace("+00:00", "Z")}
        for h in todos_huecos
    ]}

@router.post("/citas", status_code=201)
@limiter.limit("10/hour")
async def reservar(request: Request, datos: CitaEntrada):
    db_c = db.get_db()
    ajustes = await db_c["ajustes"].find_one({"_id": "ajustes"})
    reglas = await db_c["disponibilidad"].find({}).to_list(100)
    ahora_utc = datetime.now(timezone.utc)

    try:
        return await crear_cita(datos.model_dump(), ajustes, reglas, ahora_utc)
    except ValueError as e:
        msg = str(e)
        if msg == "honeypot":
            raise HTTPException(400, "Solicitud rechazada")
        if msg == "ocupado":
            raise HTTPException(409, "Ese horario ya está ocupado")
        if msg == "no_disponible":
            raise HTTPException(409, "Ese horario ya no está disponible")
        raise HTTPException(422, msg)

@router.get("/citas/{token}")
async def consultar_cita(token: str):
    cita = await db.get_db()["citas"].find_one({"token": token})
    if not cita:
        raise HTTPException(404, "Cita no encontrada")
    ajustes = await db.get_db()["ajustes"].find_one({"_id": "ajustes"})
    ahora = datetime.now(timezone.utc)
    desde = cita["inicio"] - ahora
    plazo = timedelta(hours=ajustes["plazo_cancelacion_horas"])
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(ajustes["zona_horaria"])
    return {
        "inicio": cita["inicio"].isoformat().replace("+00:00", "Z"),
        "inicio_local": cita["inicio"].astimezone(tz).strftime("%Y-%m-%dT%H:%M"),
        "fin": cita["fin"].isoformat().replace("+00:00", "Z"),
        "modalidad": cita["modalidad"],
        "tipo_sesion": cita["tipo_sesion"],
        "nombre": cita["nombre"],
        "estado": cita["estado"],
        "video_enlace": cita.get("video_enlace", ""),
        "puede_cancelar": cita["estado"] == "activa" and desde >= plazo,
        "limite_cancelacion_local": (cita["inicio"] - plazo).astimezone(tz).strftime("%Y-%m-%dT%H:%M"),
    }

@router.post("/citas/{token}/cancelar")
async def cancelar_cita(token: str):
    try:
        db_c = db.get_db()
        ajustes = await db_c["ajustes"].find_one({"_id": "ajustes"})
        ahora = datetime.now(timezone.utc)
        return await cancelar_por_paciente(token, ajustes, ahora)
    except ValueError as e:
        if str(e) == "no_encontrada":
            raise HTTPException(404, "Cita no encontrada")
        if str(e) == "fuera_plazo":
            raise HTTPException(403, "Fuera de plazo de cancelación")
        raise HTTPException(422, str(e))

@router.post("/citas/{token}/reagendar")
async def reagendar_cita(token: str, datos: ReagendarEntrada):
    db_c = db.get_db()
    cita = await db_c["citas"].find_one({"token": token, "estado": "activa"})
    if not cita:
        raise HTTPException(404, "Cita no encontrada")

    ajustes = await db_c["ajustes"].find_one({"_id": "ajustes"})
    reglas = await db_c["disponibilidad"].find({}).to_list(100)
    ahora_utc = datetime.now(timezone.utc)
    nuevo_inicio = datos.nuevo_inicio.astimezone(timezone.utc) if datos.nuevo_inicio.tzinfo else datos.nuevo_inicio.replace(tzinfo=timezone.utc)

    # Validate new slot
    from app.services.agenda import solapa
    bloqueos = await db_c["bloqueos"].find({}).to_list(100)
    citas_activas = await db_c["citas"].find({"estado": "activa", "_id": {"$ne": cita["_id"]}}).to_list(100)

    from zoneinfo import ZoneInfo
    tz = ZoneInfo(ajustes["zona_horaria"])
    dia_local = nuevo_inicio.astimezone(tz).date()
    huecos = calcular_huecos(dia_local, cita["modalidad"], ajustes, reglas, bloqueos, citas_activas, ahora_utc)

    if not any(h["inicio"] == nuevo_inicio for h in huecos):
        raise HTTPException(409, "Ese horario no está disponible")

    duracion = cita["fin"] - cita["inicio"]
    nuevo_fin = nuevo_inicio + duracion
    video = cita.get("video_enlace", "")

    await db_c["citas"].update_one(
        {"_id": cita["_id"]},
        {"$set": {"inicio": nuevo_inicio, "fin": nuevo_fin, "video_enlace": video}}
    )

    from app.services.notify import email_enviar
    from app.services.citas import _html_reagendada
    html = _html_reagendada({"inicio": nuevo_inicio, "token": token}, ajustes)
    await email_enviar(cita["email"], "Cita cambiada — Tu Espacio", html)

    return {
        "inicio": nuevo_inicio.isoformat().replace("+00:00", "Z"),
        "inicio_local": nuevo_inicio.astimezone(tz).strftime("%Y-%m-%dT%H:%M"),
        "gestion_url": f"{settings.FRONTEND_URL}/gestionar/{token}",
    }

@router.get("/citas/{token}/ics")
async def descargar_ics(token: str):
    from fastapi.responses import Response
    cita = await db.get_db()["citas"].find_one({"token": token})
    if not cita:
        raise HTTPException(404, "Cita no encontrada")
    ajustes = await db.get_db()["ajustes"].find_one({"_id": "ajustes"})
    ics = generar_ics(cita, ajustes)
    return Response(content=ics, media_type="text/calendar", headers={"Content-Disposition": f"attachment; filename=cita-{token[:8]}.ics"})

@router.post("/contacto-urgente")
@limiter.limit("3/hour")
async def contacto_urgente(request: Request, datos: ContactoUrgente):
    ahora = datetime.now(timezone.utc)
    ajustes = await db.get_db()["ajustes"].find_one({"_id": "ajustes"})
    en_horario = en_horario_laboral(ahora, ajustes)
    texto = f"🚨 Contacto urgente: {datos.nombre} ({datos.telegram})"
    await telegram_enviar(texto)
    return {"ok": True, "en_horario": en_horario}
