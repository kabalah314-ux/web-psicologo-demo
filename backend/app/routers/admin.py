from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings
from app import db
from app.schemas import CitaEntrada
from app.services.security import crear_token, verificar_token
from app.services.notify import telegram_enviar

router = APIRouter(prefix="/api/admin", tags=["admin"])
limiter = Limiter(key_func=get_remote_address)

def _limit(rate):
    if settings.modo_test:
        return lambda f: f
    return limiter.limit(rate)


@router.post("/login")
@_limit("5/minute")
async def login(request: Request, datos: dict):
    usuario = datos.get("usuario", "")
    password = datos.get("password", "")
    if usuario == settings.ADMIN_USUARIO and password == settings.ADMIN_PASSWORD:
        return {"token": crear_token(usuario)}
    raise HTTPException(401, "Credenciales inválidas")


@router.get("/citas")
async def listar_citas(usuario: str = Depends(verificar_token)):
    citas = await db.get_db()["citas"].find({}).sort("inicio", -1).to_list(200)
    return {"citas": [
        {
            "_id": str(c["_id"]),
            "inicio": c["inicio"].isoformat().replace("+00:00", "Z"),
            "fin": c["fin"].isoformat().replace("+00:00", "Z"),
            "nombre": c["nombre"],
            "email": c["email"],
            "telefono": c.get("telefono", ""),
            "tipo_sesion": c["tipo_sesion"],
            "modalidad": c["modalidad"],
            "estado": c["estado"],
        }
        for c in citas
    ]}


@router.patch("/citas/{id}")
async def actualizar_cita(id: str, datos: dict, usuario: str = Depends(verificar_token)):
    from bson import ObjectId
    try:
        oid = ObjectId(id)
    except Exception:
        raise HTTPException(422, "ID inválido")
    db_c = db.get_db()
    cita = await db_c["citas"].find_one({"_id": oid})
    if not cita:
        raise HTTPException(404, "Cita no encontrada")
    campos_permitidos = {"estado", "tipo_sesion", "modalidad"}
    actualizaciones = {k: v for k, v in datos.items() if k in campos_permitidos}
    if actualizaciones:
        await db_c["citas"].update_one({"_id": oid}, {"$set": actualizaciones})
    return {"ok": True}


@router.get("/disponibilidad")
async def obtener_disponibilidad(usuario: str = Depends(verificar_token)):
    reglas = await db.get_db()["disponibilidad"].find({}).to_list(100)
    return {"disponibilidad": [
        {
            "_id": str(r["_id"]),
            "dia_semana": r["dia_semana"],
            "hora_inicio": r["hora_inicio"],
            "hora_fin": r["hora_fin"],
            "modalidad": r.get("modalidad", ""),
        }
        for r in reglas
    ]}


@router.put("/disponibilidad")
async def actualizar_disponibilidad(datos: dict, usuario: str = Depends(verificar_token)):
    db_c = db.get_db()
    await db_c["disponibilidad"].delete_many({})
    reglas = datos.get("disponibilidad", [])
    for r in reglas:
        await db_c["disponibilidad"].insert_one(r)
    return {"ok": True, "total": len(reglas)}


@router.get("/bloqueos")
async def listar_bloqueos(usuario: str = Depends(verificar_token)):
    bloqueos = await db.get_db()["bloqueos"].find({}).to_list(100)
    return {"bloqueos": [
        {
            "_id": str(b["_id"]),
            "inicio": b["inicio"].isoformat().replace("+00:00", "Z"),
            "fin": b["fin"].isoformat().replace("+00:00", "Z"),
            "motivo": b.get("motivo", ""),
        }
        for b in bloqueos
    ]}


@router.post("/bloqueos")
async def crear_bloqueo(datos: dict, usuario: str = Depends(verificar_token)):
    from datetime import datetime as dt
    inicio = dt.fromisoformat(datos["inicio"].replace("Z", "+00:00"))
    fin = dt.fromisoformat(datos["fin"].replace("Z", "+00:00"))
    if fin <= inicio:
        raise HTTPException(422, "Fin debe ser posterior a inicio")
    doc = {
        "inicio": inicio,
        "fin": fin,
        "motivo": datos.get("motivo", ""),
    }
    result = await db.get_db()["bloqueos"].insert_one(doc)
    return {"ok": True, "_id": str(result.inserted_id)}


@router.delete("/bloqueos/{id}")
async def eliminar_bloqueo(id: str, usuario: str = Depends(verificar_token)):
    from bson import ObjectId
    try:
        oid = ObjectId(id)
    except Exception:
        raise HTTPException(422, "ID inválido")
    result = await db.get_db()["bloqueos"].delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(404, "Bloqueo no encontrado")
    return {"ok": True}


@router.get("/ajustes")
async def obtener_ajustes(usuario: str = Depends(verificar_token)):
    ajustes = await db.get_db()["ajustes"].find_one({"_id": "ajustes"})
    if not ajustes:
        raise HTTPException(404, "Ajustes no encontrados")
    ajustes.pop("_id", None)
    return ajustes


@router.put("/ajustes")
async def actualizar_ajustes(datos: dict, usuario: str = Depends(verificar_token)):
    campos_permitidos = {
        "nombre_profesional", "tipos_sesion", "modalidades",
        "plazo_cancelacion_horas", "direccion_presencial",
        "textos", "zona_horaria", "duracion_sesion_min",
        "max_citas_dia", "buffer_entre_citas_min",
    }
    actualizaciones = {k: v for k, v in datos.items() if k in campos_permitidos}
    if not actualizaciones:
        raise HTTPException(422, "Sin campos válidos para actualizar")
    # Validate plazo_cancelacion_horas
    if "plazo_cancelacion_horas" in actualizaciones:
        plazo = actualizaciones["plazo_cancelacion_horas"]
        if not isinstance(plazo, (int, float)) or plazo < 0:
            raise HTTPException(422, "plazo_cancelacion_horas inválido")
    await db.get_db()["ajustes"].update_one(
        {"_id": "ajustes"}, {"$set": actualizaciones}
    )
    return {"ok": True}


@router.post("/telegram/test")
async def test_telegram(usuario: str = Depends(verificar_token)):
    ok = await telegram_enviar("✅ Test de conexión — Tu Espacio")
    return {"ok": ok}


@router.get("/ia/estado")
async def estado_ia(usuario: str = Depends(verificar_token)):
    tiene_clave = bool(settings.OPENROUTER_API_KEY)
    modelos_raw = settings.OPENROUTER_MODELOS
    modelos = [m.strip() for m in modelos_raw.split(",") if m.strip()] if modelos_raw else []
    return {
        "is_free_tier": not tiene_clave or len(modelos) == 0,
        "modelos_disponibles": modelos,
        "openrouter_configurado": tiene_clave,
    }
