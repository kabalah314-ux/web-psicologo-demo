from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings
from app import db
from app.services.crisis import detectar_crisis
from app.services.ia import responder_ia, responder_reglas

router = APIRouter(prefix="/api/chat", tags=["chat"])
limiter = Limiter(key_func=get_remote_address)

class ChatEntrada(BaseModel):
    mensajes: list[dict] = Field(max_length=10)

@router.post("")
@limiter.limit("20/hour")
async def chat(request: Request, datos: ChatEntrada):
    for m in datos.mensajes:
        if len(m.get("contenido", "")) > 500:
            raise HTTPException(422, "Mensaje demasiado largo")

    ultimo_usuario = ""
    for m in reversed(datos.mensajes):
        if m.get("rol") == "usuario":
            ultimo_usuario = m.get("contenido", "")
            break

    if detectar_crisis(ultimo_usuario):
        ahora = datetime.now(timezone.utc)
        ajustes = await db.get_db()["ajustes"].find_one({"_id": "ajustes"})
        from app.services.crisis import en_horario_laboral
        en_horario = en_horario_laboral(ahora, ajustes)
        if en_horario:
            respuesta = ("Siento que estés pasando por un momento así. Este asistente no puede ayudarte con eso, "
                         "pero puedes avisar directamente al psicólogo ahora con el botón de abajo y te contactará lo antes posible. "
                         "Si estás en peligro inmediato, llama al 112 o al 024 (atención a la conducta suicida, 24 h, gratuito).")
        else:
            respuesta = ("Siento que estés pasando por un momento así. Ahora mismo la consulta está cerrada; "
                         "deja tu nombre y teléfono y el psicólogo te atenderá lo antes posible. "
                         "Si necesitas hablar con alguien ahora, llama al 024 (24 h, gratuito) o al 112.")
        return {"respuesta": respuesta, "tipo": "crisis", "acciones": ["contacto_urgente", "emergencias"]}

    db_c = db.get_db()
    ajustes = await db_c["ajustes"].find_one({"_id": "ajustes"})
    reglas = await db_c["disponibilidad"].find({}).to_list(100)
    bloqueos = await db_c["bloqueos"].find({}).to_list(100)
    citas = await db_c["citas"].find({"estado": "activa"}).to_list(100)
    ahora_utc = datetime.now(timezone.utc)

    from datetime import timedelta as td
    huecos_online = []
    huecos_presencial = []
    for i in range(7):
        dia = (ahora_utc + td(days=i+1)).date()
        from app.services.agenda import calcular_huecos
        h_on = calcular_huecos(dia, "online", ajustes, reglas, bloqueos, citas, ahora_utc)
        h_pr = calcular_huecos(dia, "presencial", ajustes, reglas, bloqueos, citas, ahora_utc)
        huecos_online.extend(h_on[:3])
        huecos_presencial.extend(h_pr[:3])

    contexto = {
        "nombre": ajustes["nombre_profesional"],
        "modalidades": ajustes["modalidades"],
        "tipos": ajustes["tipos_sesion"],
        "direccion": ajustes["direccion_presencial"],
        "politica": ajustes["textos"]["politica_cancelacion"],
        "huecos_online": ", ".join(f"{h['inicio_local'][-5:]}" for h in huecos_online[:5]),
        "huecos_presencial": ", ".join(f"{h['inicio_local'][-5:]}" for h in huecos_presencial[:5]),
    }

    msgs = [{"role": "user" if m["rol"] == "usuario" else "assistant", "content": m["contenido"]} for m in datos.mensajes]

    respuesta_ia = await responder_ia(msgs, contexto)

    if respuesta_ia:
        acciones = []
        if "[ABRIR_AGENDA]" in respuesta_ia:
            respuesta_ia = respuesta_ia.replace("[ABRIR_AGENDA]", "").strip()
            acciones.append("abrir_agenda")
        return {"respuesta": respuesta_ia, "tipo": "ia", "acciones": acciones}

    respuesta_reglas, acciones = responder_reglas(ultimo_usuario)
    return {"respuesta": respuesta_reglas, "tipo": "reglas", "acciones": acciones}
