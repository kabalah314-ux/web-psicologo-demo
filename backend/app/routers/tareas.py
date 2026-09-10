from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from app.config import settings
from app import db
from app.services.security import verificar_token
from app.services.notify import telegram_enviar, email_enviar

router = APIRouter(prefix="/api/tareas", tags=["tareas"])


def _verificar_cron(request: Request):
    auth = request.headers.get("authorization", "")
    token = auth.replace("Bearer ", "")
    if token != settings.CRON_SECRET:
        raise HTTPException(401, "Cron secret inválido")


@router.post("/recordatorios")
async def recordatorios(request: Request):
    _verificar_cron(request)
    db_c = db.get_db()
    ahora = datetime.now(timezone.utc)
    manana = ahora + timedelta(days=1)
    citas = await db_c["citas"].find({
        "estado": "activa",
        "inicio": {"$gte": ahora, "$lte": manana},
    }).to_list(100)

    enviados = 0
    for cita in citas:
        ajustes = await db_c["ajustes"].find_one({"_id": "ajustes"})
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(ajustes["zona_horaria"])
        inicio_local = cita["inicio"].astimezone(tz).strftime("%d/%m %H:%M")
        html = f"""
        <p>Hola {cita['nombre']},</p>
        <p>Le recordamos que tiene una sesión mañana a las {inicio_local}.</p>
        <p>Modalidad: {cita['modalidad']} — Tipo: {cita['tipo_sesion']}</p>
        <p>Si necesita cancelar o reprogramar, puede hacerlo desde su enlace de gestión.</p>
        <p>Un saludo,<br>{ajustes.get('nombre_profesional', 'Tu Espacio')}</p>
        """
        await email_enviar(cita["email"], "Recordatorio de sesión — Tu Espacio", html)
        enviados += 1

    return {"ok": True, "recordatorios_enviados": enviados}


@router.post("/resumen-diario")
async def resumen_diario(request: Request):
    _verificar_cron(request)
    db_c = db.get_db()
    ahora = datetime.now(timezone.utc)
    inicio_dia = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    fin_dia = inicio_dia + timedelta(days=1)

    citas_hoy = await db_c["citas"].find({
        "inicio": {"$gte": inicio_dia, "$lt": fin_dia},
    }).to_list(100)

    activas = [c for c in citas_hoy if c["estado"] == "activa"]
    canceladas = [c for c in citas_hoy if c["estado"] == "cancelada"]

    texto = (
        f"📊 Resumen del día:\n"
        f"Citas activas: {len(activas)}\n"
        f"Citas canceladas: {len(canceladas)}\n"
        f"Total: {len(citas_hoy)}"
    )
    await telegram_enviar(texto)

    return {"ok": True, "activas": len(activas), "canceladas": len(canceladas)}


@router.post("/purga")
async def purga(request: Request):
    _verificar_cron(request)
    db_c = db.get_db()
    hace_90_dias = datetime.now(timezone.utc) - timedelta(days=90)
    result = await db_c["citas"].delete_many({
        "estado": "cancelada",
        "inicio": {"$lt": hace_90_dias},
    })
    return {"ok": True, "eliminadas": result.deleted_count}
