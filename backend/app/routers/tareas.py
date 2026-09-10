from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Header, HTTPException
import secrets
from app.config import settings
from app import db
from app.services.notify import telegram_enviar, email_enviar
from app.services.citas import _html_recordatorio

router = APIRouter(prefix="/api/tareas", tags=["tareas"])

async def cron_requerido(x_cron_secret: str | None = Header(default=None)):
    if not x_cron_secret or not secrets.compare_digest(x_cron_secret, settings.CRON_SECRET):
        raise HTTPException(401, "Secreto incorrecto")

@router.post("/recordatorios", dependencies=[Depends(cron_requerido)])
async def recordatorios():
    ahora = datetime.now(timezone.utc)
    desde = ahora + timedelta(hours=23)
    hasta = ahora + timedelta(hours=25)
    db_c = db.get_db()
    citas = await db_c["citas"].find({
        "estado": "activa",
        "inicio": {"$gte": desde, "$lte": hasta},
        "recordatorio_enviado": False
    }).to_list(100)

    enviados = 0
    ajustes = await db_c["ajustes"].find_one({"_id": "ajustes"})
    for cita in citas:
        html = _html_recordatorio(cita, ajustes)
        ok = await email_enviar(cita["email"], "Recordatorio — Tu Espacio", html)
        if ok:
            await db_c["citas"].update_one({"_id": cita["_id"]}, {"$set": {"recordatorio_enviado": True}})
            enviados += 1

    return {"enviados": enviados}

@router.post("/resumen-diario", dependencies=[Depends(cron_requerido)])
async def resumen_diario():
    ahora = datetime.now(timezone.utc)
    db_c = db.get_db()
    ajustes = await db_c["ajustes"].find_one({"_id": "ajustes"})
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(ajustes["zona_horaria"])
    local_now = ahora.astimezone(tz)
    inicio_dia = local_now.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
    fin_dia = inicio_dia + timedelta(days=1)

    citas = await db_c["citas"].find({"estado": "activa", "inicio": {"$gte": inicio_dia, "$lt": fin_dia}}).to_list(100)
    if citas:
        lineas = [f"📅 Resumen del día ({len(citas)} citas):"]
        for c in sorted(citas, key=lambda x: x["inicio"]):
            local = c["inicio"].astimezone(tz).strftime("%H:%M")
            lineas.append(f"• {local} — {c['nombre']} ({c['modalidad']})")
        await telegram_enviar("\n".join(lineas))
    else:
        await telegram_enviar("📅 Sin citas hoy.")

    return {"citas": len(citas)}

@router.post("/purga", dependencies=[Depends(cron_requerido)])
async def purga():
    db_c = db.get_db()
    ajustes = await db_c["ajustes"].find_one({"_id": "ajustes"})
    meses = ajustes.get("retencion_meses", 12)
    limite = datetime.now(timezone.utc) - timedelta(days=meses * 30)
    resultado = await db_c["citas"].delete_many({"fin": {"$lt": limite}, "estado": {"$ne": "activa"}})
    return {"borradas": resultado.deleted_count}
