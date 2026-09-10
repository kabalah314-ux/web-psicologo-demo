from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from app.config import settings
from app import db
from app.services.security import login, crear_jwt, admin_requerido

router_login = APIRouter(prefix="/api/admin", tags=["admin-login"])
router_admin = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(admin_requerido)])

class LoginEntrada(BaseModel):
    usuario: str
    password: str

@router_login.post("/login")
async def login_admin(datos: LoginEntrada):
    if not login(datos.usuario, datos.password):
        raise HTTPException(401, "Credenciales incorrectas")
    return {"token": crear_jwt(), "expira_en": "12h"}

@router_admin.get("/citas")
async def admin_citas(desde: str = None, hasta: str = None):
    q = {}
    if desde:
        q["inicio"] = {"$gte": datetime.fromisoformat(desde.replace("Z", "+00:00"))}
    if hasta:
        q.setdefault("inicio", {})["$lte"] = datetime.fromisoformat(hasta.replace("Z", "+00:00"))
    citas = await db.get_db()["citas"].find(q).sort("inicio", 1).to_list(1000)
    return [{"id": str(c["_id"]), "token": c["token"], "nombre": c["nombre"], "email": c["email"],
             "telefono": c.get("telefono", ""), "inicio": c["inicio"].isoformat(), "fin": c["fin"].isoformat(),
             "modalidad": c["modalidad"], "tipo_sesion": c["tipo_sesion"], "estado": c["estado"]} for c in citas]

class PatchCita(BaseModel):
    estado: str | None = None
    nuevo_inicio: datetime | None = None

@router_admin.patch("/citas/{cita_id}")
async def patch_cita(cita_id: str, datos: PatchCita):
    from bson import ObjectId
    db_c = db.get_db()
    cita = await db_c["citas"].find_one({"_id": ObjectId(cita_id)})
    if not cita:
        raise HTTPException(404, "Cita no encontrada")

    ahora = datetime.now(timezone.utc)
    update = {}

    if datos.estado:
        update["estado"] = datos.estado
        update["cancelado_en"] = ahora
        update["cancelado_por"] = "admin"

    if datos.nuevo_inicio:
        nuevo = datos.nuevo_inicio.astimezone(timezone.utc) if datos.nuevo_inicio.tzinfo else datos.nuevo_inicio.replace(tzinfo=timezone.utc)
        duracion = cita["fin"] - cita["inicio"]
        update["inicio"] = nuevo
        update["fin"] = nuevo + duracion

    await db_c["citas"].update_one({"_id": ObjectId(cita_id)}, {"$set": update})

    if datos.estado == "cancelada" or datos.nuevo_inicio:
        ajustes = await db_c["ajustes"].find_one({"_id": "ajustes"})
        from app.services.notify import email_enviar
        from app.services.citas import _html_cancelacion, _html_reagendada
        if datos.estado == "cancelada":
            html = _html_cancelacion(cita, ajustes)
            await email_enviar(cita["email"], "Cita cancelada — Tu Espacio", html)
        elif datos.nuevo_inicio:
            html = _html_reagendada({"inicio": datos.nuevo_inicio, "token": cita["token"]}, ajustes)
            await email_enviar(cita["email"], "Cita cambiada — Tu Espacio", html)

    return {"ok": True}

@router_admin.get("/disponibilidad")
async def get_disponibilidad():
    reglas = await db.get_db()["disponibilidad"].find({}).to_list(100)
    return [{"id": str(r["_id"]), "dia_semana": r["dia_semana"], "inicio": r["inicio"], "fin": r["fin"], "modalidades": r["modalidades"]} for r in reglas]

class ReglaDisponibilidad(BaseModel):
    dia_semana: int
    inicio: str
    fin: str
    modalidades: list[str]

class PutDisponibilidad(BaseModel):
    reglas: list[ReglaDisponibilidad]

@router_admin.put("/disponibilidad")
async def put_disponibilidad(datos: PutDisponibilidad):
    for r in datos.reglas:
        if r.inicio >= r.fin:
            raise HTTPException(422, f"Inicio debe ser menor que fin para día {r.dia_semana}")
    db_c = db.get_db()
    await db_c["disponibilidad"].delete_many({})
    await db_c["disponibilidad"].insert_many([r.model_dump() for r in datos.reglas])
    return {"ok": True, "reglas": len(datos.reglas)}

@router_admin.get("/bloqueos")
async def get_bloqueos():
    bloq = await db.get_db()["bloqueos"].find({}).sort("inicio", 1).to_list(100)
    return [{"id": str(b["_id"]), "inicio": b["inicio"].isoformat(), "fin": b["fin"].isoformat(), "motivo": b.get("motivo", "")} for b in bloq]

class BloqueoEntrada(BaseModel):
    inicio: datetime
    fin: datetime
    motivo: str = ""

@router_admin.post("/bloqueos", status_code=201)
async def crear_bloqueo(datos: BloqueoEntrada):
    ini = datos.inicio.astimezone(timezone.utc) if datos.inicio.tzinfo else datos.inicio.replace(tzinfo=timezone.utc)
    fin = datos.fin.astimezone(timezone.utc) if datos.fin.tzinfo else datos.fin.replace(tzinfo=timezone.utc)
    await db.get_db()["bloqueos"].insert_one({"inicio": ini, "fin": fin, "motivo": datos.motivo})
    return {"ok": True}

@router_admin.delete("/bloqueos/{bloqueo_id}")
async def eliminar_bloqueo(bloqueo_id: str):
    from bson import ObjectId
    await db.get_db()["bloqueos"].delete_one({"_id": ObjectId(bloqueo_id)})
    return {"ok": True}

@router_admin.get("/ajustes")
async def get_ajustes():
    a = await db.get_db()["ajustes"].find_one({"_id": "ajustes"})
    return {k: v for k, v in a.items() if k != "_id"}

@router_admin.put("/ajustes")
async def put_ajustes(datos: dict):
    if datos.get("plazo_cancelacion_horas", 0) < 0:
        raise HTTPException(422, "Plazo de cancelación no puede ser negativo")
    if datos.get("duracion_min", 0) < 15:
        raise HTTPException(422, "Duración mínima 15 minutos")
    await db.get_db()["ajustes"].update_one({"_id": "ajustes"}, {"$set": datos})
    return {"ok": True}

@router_admin.post("/telegram/test")
async def telegram_test():
    from app.services.notify import telegram_enviar
    ok = await telegram_enviar("Prueba OK")
    return {"ok": ok}

@router_admin.get("/ia/estado")
async def ia_estado():
    from app.services.ia import estado_openrouter
    return await estado_openrouter()
