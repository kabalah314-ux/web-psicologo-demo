from motor.motor_asyncio import AsyncIOMotorClient
from datetime import timezone
from app.config import settings

_cliente = None

def get_cliente():
    global _cliente
    if _cliente is None:
        _cliente = AsyncIOMotorClient(settings.MONGO_URI, tz_aware=True)
    return _cliente

def get_db():
    return get_cliente()[settings.MONGO_DB]

def cerrar():
    global _cliente
    if _cliente:
        _cliente.close()
        _cliente = None

def a_utc(dt):
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

async def crear_indices():
    db = get_db()
    await db["citas"].create_index(
        [("inicio", 1)],
        unique=True,
        partialFilterExpression={"estado": "activa"},
        name="citas_inicio_activa"
    )
    await db["citas"].create_index([("token", 1)], unique=True, name="citas_token")
    await db["citas"].create_index([("email", 1)], name="citas_email")
    await db["citas"].create_index([("estado", 1), ("inicio", 1)], name="citas_estado_inicio")
    await db["bloqueos"].create_index([("inicio", 1)], name="bloqueos_inicio")

async def sembrar_defecto():
    db = get_db()
    if await db["ajustes"].count_documents({}) == 0:
        await db["ajustes"].insert_one({
            "_id": "ajustes",
            "nombre_profesional": "Nombre Apellidos",
            "zona_horaria": "Europe/Madrid",
            "duracion_min": 50,
            "buffer_min": 10,
            "antelacion_min_horas": 12,
            "plazo_cancelacion_horas": 24,
            "dias_vista": 30,
            "tipos_sesion": [
                {"id": "primera", "nombre": "Primera sesión", "duracion_min": 50, "precio_texto": "Tarifa por definir"},
                {"id": "seguimiento", "nombre": "Seguimiento", "duracion_min": 50, "precio_texto": "Tarifa por definir"}
            ],
            "modalidades": ["online", "presencial"],
            "direccion_presencial": "Por definir",
            "video_modo": "fijo",
            "video_enlace_fijo": "",
            "telegram_chat_id": "",
            "horario_laboral": {"dias": [0, 1, 2, 3, 4], "inicio": "09:00", "fin": "20:00"},
            "telefono_contacto_urgente": "",
            "retencion_meses": 12,
            "textos": {
                "politica_cancelacion": "Puedes cancelar o cambiar tu cita hasta 24 h antes desde el enlace de tu email."
            }
        })
    if await db["disponibilidad"].count_documents({}) == 0:
        reglas = []
        for dia in range(5):  # lunes a viernes
            reglas.append({"dia_semana": dia, "inicio": "09:00", "fin": "14:00", "modalidades": ["online", "presencial"]})
            reglas.append({"dia_semana": dia, "inicio": "16:00", "fin": "20:00", "modalidades": ["online", "presencial"]})
        await db["disponibilidad"].insert_many(reglas)
