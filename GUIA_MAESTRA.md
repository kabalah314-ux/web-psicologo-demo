# GUIA MAESTRA v2 — Tu Espacio · Psicología

Prototipo estático → sistema real de citas · React + FastAPI + MongoDB · Render (gratis) + Vercel · OpenRouter gratuito · MiMo Code en terminal

---

## 0. Protocolo de trabajo

### Humano:

- Crea las cuentas de la sección 2. Sin MONGO_URI no se pasa ni la Fase 0.
- Cada sesión con MiMo Code empieza pegando el contenido de HARNESS/PROMPT_SESION.md.
- MiMo trabaja una fase a la vez y solo avanza cuando python HARNESS/check.py está todo en PASS.
- Lo que una máquina no puede comprobar (te llegó el Telegram, el email, se ve bien en el móvil) está en HARNESS/MANUAL_0X.md; lo haces tú al cerrar cada fase.
- Revisa el git diff antes de cada commit de fase. Busca sobre todo tests con aserciones cambiadas.

### MiMo Code:

- Lee HARNESS/STATE.md antes de tocar nada. Trabaja solo en FASE_ACTUAL.
- Nombres de ficheros, rutas, campos, colecciones y variables: exactamente como aquí. El arnés los comprueba literalmente.
- Tras cada cambio: python HARNESS/check.py. Arregla el primer FAIL. Repite.
- 3 intentos seguidos en FAIL sobre el mismo criterio → para, escribe en NOTAS de STATE.md qué probaste y pregunta.
- Nunca arregles un test cambiando la aserción. Nunca edites HARNESS/check.py ni HARNESS/checks/*.
- Ejecuta tú los comandos; no pidas al humano que lo haga.

---

## 1. Decisiones bloqueadas

Ver [DECISIONES.md](DECISIONES.md) — no se cambian sin autorización escrita del humano.

---

## 2. Cuentas y claves

| Servicio | Pasos | Variables |
|----------|-------|-----------|
| MongoDB Atlas | Cluster M0 → Database Access (usuario+pass) → Network Access 0.0.0.0/0 → Connect → Drivers → URI | MONGO_URI |
| Telegram | @BotFather → /newbot → token. El psicólogo escribe "hola" al bot → abrir getUpdates → message.chat.id | TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID |
| Resend | API Key. Sin dominio verificado solo envía al email de tu cuenta desde onboarding@resend.dev | RESEND_API_KEY, EMAIL_FROM |
| OpenRouter | Key. Cuenta sin crédito: tope diario de peticiones a modelos :free. Elige 3 modelos :free | OPENROUTER_API_KEY, OPENROUTER_MODELOS |
| Render | Cuenta gratis conectada a GitHub. Se configura en Fase 6 | API_URL_PROD |
| cron-job.org | Cuenta gratis. Fase 6 | CRON_SECRET |

---

## 3. Estructura del repositorio (exacta)

```
tu-espacio/
├── DECISIONES.md · GUIA_MAESTRA.md · CHECKLIST_CLIENTE.md · .gitignore
├── HARNESS/
│   ├── STATE.md · PROMPT_SESION.md · check.py
│   ├── checks/ __init__.py · fase0.py … fase6.py
│   └── MANUAL_00.md … MANUAL_06.md
├── backend/
│   ├── requirements.txt · .env.example · .env (no se commitea) · pytest.ini
│   ├── app/
│   │   ├── __init__.py · main.py · config.py · db.py · schemas.py
│   │   ├── services/ __init__.py · agenda.py · citas.py · notify.py · ics.py · video.py · crisis.py · ia.py · security.py
│   │   └── routers/ __init__.py · publico.py · chat.py · admin.py · tareas.py
│   └── tests/ conftest.py · test_agenda.py · test_crisis.py · test_citas.py · test_admin.py · test_ia.py
└── frontend/
    ├── package.json · vite.config.ts · tsconfig.json · index.html · vercel.json · .env.example
    └── src/
        ├── main.tsx · App.tsx · api.ts · tipos.ts · estilos.css
        ├── pages/ Home.tsx · Gestionar.tsx · Admin.tsx
        └── components/ Hero.tsx · Areas.tsx · Profesional.tsx · ComoFunciona.tsx · Sesiones.tsx · Faq.tsx
            · ModalReserva.tsx · Chat.tsx
            · admin/ Login.tsx · AgendaSemana.tsx · Disponibilidad.tsx · Bloqueos.tsx · Ajustes.tsx
```

---

## 4. Modelo de datos (base tuespacio)

### ajustes — documento único _id: "ajustes"

```json
{
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
  "horario_laboral": {"dias": [0,1,2,3,4], "inicio": "09:00", "fin": "20:00"},
  "telefono_contacto_urgente": "",
  "retencion_meses": 12,
  "textos": {"politica_cancelacion": "Puedes cancelar o cambiar tu cita hasta 24 h antes desde el enlace de tu email."}
}
```

dia_semana: 0 = lunes … 6 = domingo (datetime.weekday()).

### disponibilidad

```json
{"dia_semana": 0, "inicio": "09:00", "fin": "14:00", "modalidades": ["online", "presencial"]}
```

Semilla: L–V 09:00–14:00 y 16:00–20:00 (10 documentos).

### bloqueos

```json
{"inicio": <UTC>, "fin": <UTC>, "motivo": "Vacaciones"}
```

### citas

```json
{
  "inicio": <UTC>, "fin": <UTC>,
  "modalidad": "online", "tipo_sesion": "primera",
  "nombre": "…", "email": "…", "telefono": "",
  "estado": "activa",
  "token": "<token_urlsafe(32)>", "video_enlace": "",
  "creado_en": <UTC>,
  "cancelado_en": null, "cancelado_por": null,
  "recordatorio_enviado": false
}
```

estado ∈ activa | cancelada | no_show | completada.

### Índices (db.crear_indices(), llamada en el lifespan)

- citas: [("inicio",1)] unique, partialFilterExpression={"estado":"activa"} ← anti doble reserva.
- citas: [("token",1)] unique · [("email",1)] · [("estado",1),("inicio",1)].
- bloqueos: [("inicio",1)].

---

## 5. Contratos de la API

Fechas ISO 8601 con Z. Errores `{"detail":"…"}`.

### /api/publico

| Ruta | Entrada → Salida | Errores |
|------|-------------------|---------|
| GET /config | → {nombre_profesional,tipos_sesion,modalidades,plazo_cancelacion_horas,direccion_presencial,textos,zona_horaria} | — |
| GET /huecos?modalidad=&desde=YYYY-MM-DD&dias=14 | → {"huecos":[{"inicio":"…Z","inicio_local":"YYYY-MM-DDTHH:MM","fin":"…Z"}]} | 422 modalidad inválida o dias>30 |
| POST /citas | {inicio,modalidad,tipo_sesion,nombre,email,telefono?,consentimiento:true,website:""} → 201 {id,inicio,inicio_local,modalidad,gestion_url,video_enlace} | 400 honeypot · 409 ocupado/no disponible · 422 validación · 429 >10/h/IP |
| GET /citas/{token} | → {inicio,inicio_local,fin,modalidad,tipo_sesion,nombre,estado,video_enlace,puede_cancelar,limite_cancelacion_local} | 404 |
| POST /citas/{token}/cancelar | → {"ok":true} | 403 fuera de plazo (+ Telegram) · 404 · 409 ya cancelada |
| POST /citas/{token}/reagendar | {nuevo_inicio} → {inicio,inicio_local,gestion_url} | 403 · 404 · 409 |
| GET /citas/{token}/ics | → text/calendar | 404 |
| POST /contacto-urgente | {nombre,telefono} → {"ok":true,"en_horario":bool} (+ Telegram) | 429 >3/h/IP |

### /api/chat

POST {"mensajes":[{"rol":"usuario"|"asistente","contenido":"…"}]} (máx 10 mensajes, 500 chars c/u) → {"respuesta":"…","tipo":"ia"|"reglas"|"crisis","acciones":["abrir_agenda"|"contacto_urgente"|"emergencias"]}. 20/h/IP → 429.

### /api/admin

| Ruta | Detalle |
|------|---------|
| POST /login {usuario,password} → {token,expira_en} | 401 si falla |
| GET /citas?desde=&hasta= | lista con email/teléfono |
| PATCH /citas/{id} {estado} o {nuevo_inicio} | cancelar/no_show/completada/reagendar; sin regla de plazo; cancelado_por:"admin"; email al paciente |
| GET /disponibilidad · PUT /disponibilidad {"reglas":[…]} | PUT reemplaza todo; 422 si inicio>=fin |
| GET /bloqueos · POST /bloqueos · DELETE /bloqueos/{id} | |
| GET /ajustes · PUT /ajustes | 422 si plazo_cancelacion_horas<0, duracion_min<15, zona horaria inválida |
| POST /telegram/test | envía "Prueba OK" |
| GET /ia/estado | llama GET openrouter.ai/api/v1/key → {is_free_tier,limit_remaining,usage,modelos:[…]}; si falla → {"error":"…"} con 200 |

### /api/tareas

Cabecera X-Cron-Secret, 401 si falta o no coincide.

| Ruta | Detalle |
|------|---------|
| POST /recordatorios | citas activas con inicio en [ahora+23h, ahora+25h] y recordatorio_enviado=false → email → marcar. {"enviados":n} |
| POST /resumen-diario | Telegram con citas de hoy (hora local). {"citas":n} |
| POST /purga | borra citas con fin < ahora − retencion_meses·30 días. {"borradas":n} |

### /api/salud

GET → {"ok":true}

---

## 6. Algoritmos (implementar exactamente así)

### 6.1 db.py

```python
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

async def crear_indices(): ...   # sección 4

async def sembrar_defecto(): ... # inserta ajustes y las 10 reglas solo si no existen
```

`tz_aware=True` hace que Mongo devuelva datetimes aware; `a_utc` es la red por si acaso. El lifespan de main.py llama a `crear_indices()` y `sembrar_defecto()` al arrancar y `cerrar()` al apagar.

### 6.2 services/agenda.py

```python
from datetime import datetime, timedelta, date, time, timezone
from zoneinfo import ZoneInfo

def solapa(a_ini, a_fin, b_ini, b_fin) -> bool:
    return a_ini < b_fin and b_ini < a_fin

def calcular_huecos(dia: date, modalidad: str, ajustes: dict, reglas: list, bloqueos: list,
                    citas_activas: list, ahora_utc: datetime) -> list[dict]:
    tz = ZoneInfo(ajustes["zona_horaria"])
    dur = timedelta(minutes=ajustes["duracion_min"])
    paso = timedelta(minutes=ajustes["duracion_min"] + ajustes["buffer_min"])
    minimo = ahora_utc + timedelta(hours=ajustes["antelacion_min_horas"])
    huecos = []
    for r in reglas:
        if r["dia_semana"] != dia.weekday() or modalidad not in r["modalidades"]:
            continue
        t = datetime.combine(dia, time.fromisoformat(r["inicio"]), tzinfo=tz)
        fin_regla = datetime.combine(dia, time.fromisoformat(r["fin"]), tzinfo=tz)
        while t + dur <= fin_regla:
            ini, fin = t.astimezone(timezone.utc), (t + dur).astimezone(timezone.utc)
            libre = ini >= minimo \
                and not any(solapa(ini, fin, b["inicio"], b["fin"]) for b in bloqueos) \
                and not any(solapa(ini, fin, c["inicio"], c["fin"]) for c in citas_activas)
            if libre:
                huecos.append({"inicio": ini, "fin": fin, "inicio_local": t.strftime("%Y-%m-%dT%H:%M")})
            t += paso
    return sorted(huecos, key=lambda h: h["inicio"])
```

### 6.3 services/citas.py

- `website != ""` → 400.
- Convertir inicio a UTC; calcular dia_local; si inicio no está en `calcular_huecos(dia_local, …)` → 409 "Ese horario ya no está disponible".
- Documento con `token = secrets.token_urlsafe(32)`, `video_enlace = enlace_video(ajustes, token)` si online, `fin = inicio + duracion` del tipo_sesion.
- `insert_one` dentro de `try/except pymongo.errors.DuplicateKeyError` → 409.
- Después del insert: `await email_enviar(...)` y `await telegram_enviar(...)`, cada uno en su `try/except Exception: logging.exception(...)`. Un fallo de notificación no deshace la cita.
- `gestion_url = f"{settings.FRONTEND_URL}/gestionar/{token}"`.
- `puede_cancelar(cita, ajustes, ahora)` = `cita["estado"]=="activa"` and `cita["inicio"] - ahora >= timedelta(hours=ajustes["plazo_cancelacion_horas"])`.
- `cancelar_por_paciente`: si no puede → Telegram "⚠️ Solicitud de cancelación fuera de plazo: {nombre} {fecha local}" y 403.
- reagendar: valida el nuevo hueco igual que crear; actualiza inicio/fin/video_enlace; DuplicateKeyError → 409; email "cita cambiada".

### 6.4 services/video.py

```python
def enlace_video(ajustes, token):
    return f"https://meet.jit.si/TuEspacio-{token[:16]}" if ajustes["video_modo"] == "jitsi" else ajustes.get("video_enlace_fijo", "")
```

### 6.5 services/notify.py

```python
ENVIADOS: list[dict] = []   # solo se llena en MODO_TEST

async def telegram_enviar(texto: str) -> bool:
    if settings.MODO_TEST:
        ENVIADOS.append({"canal": "telegram", "texto": texto})
        return True
    chat_id = settings.TELEGRAM_CHAT_ID
    if not settings.TELEGRAM_BOT_TOKEN or not chat_id:
        return False
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.post(f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                         json={"chat_id": chat_id, "text": texto, "parse_mode": "HTML"})
    return r.status_code == 200

async def email_enviar(para: str, asunto: str, html: str, ics: str | None = None) -> bool:
    if settings.MODO_TEST:
        ENVIADOS.append({"canal": "email", "para": para, "asunto": asunto, "texto": html})
        return True
    payload = {"from": settings.EMAIL_FROM, "to": [para], "subject": asunto, "html": html}
    if ics:
        payload["attachments"] = [{"filename": "cita.ics", "content": base64.b64encode(ics.encode()).decode()}]
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.post("https://api.resend.com/emails",
                         headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"}, json=payload)
    return r.status_code in (200, 201)
```

Plantillas: `html_confirmacion`, `html_cancelacion`, `html_reagendada`, `html_recordatorio` (fecha local, modalidad, dirección o enlace vídeo, gestion_url, política de cancelación).

### 6.6 services/crisis.py

```python
import unicodedata, re
from zoneinfo import ZoneInfo

PATRONES = ["suicid", "quitarme la vida", "no quiero vivir", "hacerme daño", "acabar con todo", "matarme",
            "morirme", "me quiero morir", "autolesion", "no aguanto mas", "no puedo mas", "sobredosis"]

def normalizar(t: str) -> str:
    return re.sub(r"[\u0300-\u036f]", "", unicodedata.normalize("NFD", t.lower()))

_PN = [normalizar(p) for p in PATRONES]

def detectar_crisis(texto: str) -> bool:
    n = normalizar(texto)
    return any(p in n for p in _PN)

def en_horario_laboral(ahora_utc, ajustes) -> bool:
    local = ahora_utc.astimezone(ZoneInfo(ajustes["zona_horaria"]))
    h = ajustes["horario_laboral"]
    return local.weekday() in h["dias"] and h["inicio"] <= local.strftime("%H:%M") < h["fin"]
```

Respuestas (tipo:"crisis", acciones:["contacto_urgente","emergencias"]):

- **En horario:** "Siento que estés pasando por un momento así. Este asistente no puede ayudarte con eso, pero puedes avisar directamente al psicólogo ahora con el botón de abajo y te contactará lo antes posible. Si estás en peligro inmediato, llama al 112 o al 024 (atención a la conducta suicida, 24 h, gratuito)."
- **Fuera de horario:** "Siento que estés pasando por un momento así. Ahora mismo la consulta está cerrada; deja tu nombre y teléfono y el psicólogo te atenderá lo antes posible. Si necesitas hablar con alguien ahora, llama al 024 (24 h, gratuito) o al 112."

### 6.7 services/ia.py

```python
SYSTEM = """Eres el asistente administrativo de la consulta de psicología "{nombre}". Solo respondes sobre: cómo reservar, modalidades (online/presencial), duración y tarifas, primera sesión, política de cancelación, horarios disponibles.
No das consejo psicológico, no diagnosticas ni opinas sobre síntomas: si te preguntan algo clínico, di que eso se trata en sesión y ofrece reservar.
No pidas ni repitas datos personales. Español, máximo 4 frases, tono cercano. Si procede reservar, termina con la etiqueta exacta [ABRIR_AGENDA].
Datos: modalidades {modalidades}; sesiones {tipos}; dirección presencial {direccion}; cancelación: {politica}.
Próximos huecos online: {huecos_online}. Próximos huecos presenciales: {huecos_presencial}."""

MOCK = {"respuesta": None, "llamadas": 0}          # usado solo en MODO_TEST
_cache_modelos = {"ts": 0, "lista": []}

async def modelos_gratis() -> list[str]:
    if settings.OPENROUTER_MODELOS:
        return [m.strip() for m in settings.OPENROUTER_MODELOS.split(",") if m.strip()]
    # si no: GET https://openrouter.ai/api/v1/models, filtrar id.endswith(":free"), cachear 1 h, máx 5

async def responder_ia(mensajes: list[dict], contexto: dict) -> str | None:
    if settings.MODO_TEST:
        MOCK["llamadas"] += 1
        return MOCK["respuesta"]
    if not settings.OPENROUTER_API_KEY:
        return None
    cuerpo_sys = SYSTEM.format(**contexto)
    async with httpx.AsyncClient(timeout=20) as c:
        for modelo in await modelos_gratis():
            try:
                r = await c.post("https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                             "HTTP-Referer": settings.FRONTEND_URL, "X-Title": "Tu Espacio"},
                    json={"model": modelo, "messages": [{"role": "system", "content": cuerpo_sys}, *mensajes],
                          "max_tokens": 300, "temperature": 0.3})
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
                logging.warning("OpenRouter %s → %s", modelo, r.status_code)
            except httpx.HTTPError as e:
                logging.warning("OpenRouter %s error %s", modelo, e)
    return None

def responder_reglas(texto: str) -> tuple[str, list[str]]:
    # diccionario palabra clave → respuesta
    # sin coincidencia: ("Puedo ayudarte con dudas sobre reservas, modalidades y tarifas. ¿Quieres abrir la agenda?", ["abrir_agenda"])

async def estado_openrouter() -> dict:
    # GET https://openrouter.ai/api/v1/key → {"is_free_tier": ..., "limit_remaining": ..., "usage": ..., "modelos": [...]}
    # excepción → {"error": str(e)}
```

Mensajes se mapea usuario→user, asistente→assistant. Contexto de huecos: 5 primeros de los próximos 7 días por modalidad, formateados "lun 04/05 09:00".

Orden en routers/chat.py: rate limit → validar (Pydantic) → detectar_crisis(último mensaje del usuario) → responder_ia → si None, responder_reglas. Si la respuesta IA contiene [ABRIR_AGENDA], se quita y se añade abrir_agenda.

### 6.8 services/security.py

```python
bearer = HTTPBearer(auto_error=False)

def login(usuario, password) -> bool:
    return secrets.compare_digest(usuario, settings.ADMIN_USUARIO) and secrets.compare_digest(password, settings.ADMIN_PASSWORD)

def crear_jwt():
    return jwt.encode({"sub": "admin", "exp": datetime.now(timezone.utc) + timedelta(hours=12)},
                      settings.JWT_SECRET, algorithm="HS256")

async def admin_requerido(cred: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if cred is None:
        raise HTTPException(401, "No autenticado")
    try:
        jwt.decode(cred.credentials, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Token inválido o caducado")

async def cron_requerido(x_cron_secret: str | None = Header(default=None)):
    if not x_cron_secret or not secrets.compare_digest(x_cron_secret, settings.CRON_SECRET):
        raise HTTPException(401, "Secreto incorrecto")
```

### 6.9 Rate limit (slowapi)

`limiter = Limiter(key_func=get_remote_address)` en main.py, `app.state.limiter = limiter`, handler de RateLimitExceeded → 429. Decoradores `@limiter.limit("20/hour")` en chat, `"10/hour"` en POST citas, `"3/hour"` en contacto-urgente. Los tests hacen `app.state.limiter.reset()` antes de cada test.

---

## 7. Configuración

### backend/.env.example

```
MONGO_URI=mongodb+srv://usuario:pass@cluster.mongodb.net
MONGO_DB=tuespacio
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173
API_URL_PROD=
ADMIN_USUARIO=admin
ADMIN_PASSWORD=cambiame-ya
JWT_SECRET=cambiame-32-caracteres-aleatorios
CRON_SECRET=cambiame-32-caracteres-aleatorios
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
RESEND_API_KEY=
EMAIL_FROM=Tu Espacio <onboarding@resend.dev>
OPENROUTER_API_KEY=
OPENROUTER_MODELOS=
MODO_TEST=false
```

`config.py`: `class Settings(BaseSettings)` con esos campos, `model_config = SettingsConfigDict(env_file=".env", extra="ignore")`; `settings = Settings()`. CORS_ORIGINS se separa por comas.

### backend/requirements.txt

```
fastapi
uvicorn[standard]
motor
pydantic[email]
pydantic-settings
httpx
PyJWT
slowapi
pytest
pytest-asyncio
asgi-lifespan
```

### backend/pytest.ini

```ini
[pytest]
asyncio_mode = auto
env_override_existing_values = 1
```

### frontend/vercel.json

```json
{"rewrites": [{"source": "/(.*)", "destination": "/index.html"}]}
```

### frontend/.env.example

```
VITE_API_URL=http://localhost:8000
```

### backend/tests/conftest.py (esqueleto obligatorio)

```python
import os
os.environ["MODO_TEST"] = "true"
os.environ["MONGO_DB"] = "tuespacio_test"   # ANTES de importar app

import pytest, httpx
from asgi_lifespan import LifespanManager
from app.main import app
from app import db
from app.services import notify, ia

@pytest.fixture
async def cliente():
    async with LifespanManager(app):
        d = db.get_db()
        for col in ("citas", "bloqueos", "disponibilidad", "ajustes"):
            await d[col].delete_many({})
        await db.sembrar_defecto()
        notify.ENVIADOS.clear()
        ia.MOCK.update(respuesta=None, llamadas=0)
        app.state.limiter.reset()
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
            yield c
    db.cerrar()

@pytest.fixture
async def token_admin(cliente):
    r = await cliente.post("/api/admin/login", json={
        "usuario": os.environ.get("ADMIN_USUARIO", "admin"),
        "password": os.environ.get("ADMIN_PASSWORD", "cambiame-ya")
    })
    return r.json()["token"]
```

Los tests leen ADMIN_USUARIO/ADMIN_PASSWORD del .env real vía settings (importar `from app.config import settings` y usar esos valores; no hardcodear).

---

## 8. FASES

### FASE 0 — Esqueleto y arnés

1. git init; estructura de la sección 3 (carpetas + `__init__.py`); .gitignore con `.env node_modules __pycache__ dist .venv .pytest_cache`; DECISIONES.md; CHECKLIST_CLIENTE.md.
2. Backend: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`. config.py, db.py (6.1 completo), main.py con lifespan, CORS, GET /api/salud. Copiar .env.example → .env y rellenar MONGO_URI, contraseñas y secretos.
3. Frontend: `npm create vite@latest frontend -- --template react-ts`, `npm i react-router-dom`. App.tsx con rutas /, /gestionar/:token, /admin y páginas vacías. vercel.json, .env.example.
4. Crear HARNESS/ completo (parte B). Ejecutar `python HARNESS/check.py`.

### FASE 1 — Motor de agenda

1. db.crear_indices() y db.sembrar_defecto() completos.
2. services/agenda.py (6.2), crisis.py (6.6), video.py (6.4), ics.py: generar_ics(cita, ajustes) -> str con BEGIN:VCALENDAR, VERSION:2.0, PRODID, BEGIN:VEVENT, UID:{token}, DTSTAMP, DTSTART:YYYYMMDDTHHMMSSZ, DTEND, SUMMARY:Sesión de psicología, DESCRIPTION: (enlace gestión y vídeo), END:VEVENT, END:VCALENDAR, líneas con \r\n.
3. tests/test_agenda.py con ajustes de la sección 4, reglas de la semilla, ahora = 2026-04-01T00:00Z salvo donde se indica:
   - Lunes 2026-05-04 sin nada → 9 huecos, inicio_local de 09:00,10:00,11:00,12:00,13:00,16:00,17:00,18:00,19:00.
   - Cita activa 10:00–10:50 local → 8 huecos y ninguno solapa con ella.
   - Bloqueo 09:00–14:00 local → 4 huecos.
   - ahora = 2026-05-04T06:00Z (08:00 local), antelación 12 h → 0 huecos.
   - Sábado 2026-05-09 → 0. Modalidad presencial con reglas solo online → 0.
   - DST: lunes 2026-03-30 (CEST) primer hueco inicio == 2026-03-30T07:00Z; viernes 2026-03-27 (CET) primer hueco == 2026-03-27T08:00Z.
   - solapa: adyacentes (fin == inicio) → False; contenido → True.
   - generar_ics contiene BEGIN:VEVENT y UID:.
4. tests/test_crisis.py: "me quiero morir"→True; "quiero reservar"→False; "SUICIDIO"→True; "No aguanto más"→True; en_horario_laboral: martes 2026-05-05T08:00Z (10:00 local)→True; domingo→False; martes 18:00Z (20:00 local)→False.

### FASE 2 — API pública + notificaciones

1. schemas.py: CitaEntrada, ReagendarEntrada, ContactoUrgente.
2. notify.py (6.5) + plantillas. citas.py (6.3). routers/publico.py con las 8 rutas. Rate limits (6.9).
3. tests/conftest.py (sección 7). tests/test_citas.py, helper primer_hueco(cliente, modalidad):
   - /huecos devuelve ≥1 y todos los inicio terminan en Z.
   - POST /citas válido → 201, gestion_url contiene /gestionar/, ENVIADOS tiene 1 email y 1 telegram.
   - Mismo inicio → 409.
   - Concurrencia: asyncio.gather de 2 POST al mismo hueco → exactamente {201, 409}.
   - website:"x" → 400 · consentimiento:false → 422 · email inválido → 422 · dias=31 → 422.
   - GET /citas/{token} → puede_cancelar True (cita a ≥2 días).
   - Cita insertada directamente en BD con inicio = ahora+10h → cancelar → 403 y ENVIADOS tiene un telegram con "fuera de plazo".
   - Cancelar en plazo → 200; el hueco reaparece en /huecos; segunda cancelación → 409.
   - reagendar a otro hueco → 200 y el antiguo vuelve a estar libre; reagendar sobre hueco ocupado → 409.
   - /ics → 200, content-type empieza por text/calendar, cuerpo contiene BEGIN:VEVENT.
   - contacto-urgente → 200 con en_horario bool y 1 telegram.

### FASE 3 — API admin + tareas

1. security.py (6.8). routers/admin.py: router admin_login y router admin con dependencies=[Depends(admin_requerido)]. GET /ia/estado se implementa aquí llamando a ia.estado_openrouter() (en MODO_TEST devuelve {"is_free_tier": True, "limit_remaining": 0, "usage": 0, "modelos": []}).
2. routers/tareas.py con dependencies=[Depends(cron_requerido)].
3. tests/test_admin.py:
   - login incorrecto → 401; correcto → token.
   - GET /api/admin/citas sin token → 401; con token inventado → 401.
   - PUT /disponibilidad con inicio >= fin → 422; válido → GET /huecos refleja el cambio.
   - POST /bloqueos → /huecos lo respeta; DELETE → vuelve.
   - PATCH /citas/{id} {estado:"no_show"} → 200; {estado:"cancelada"} → email en ENVIADOS; {nuevo_inicio} → 200 (sin regla de plazo aunque la cita sea en 2 h).
   - PUT /ajustes con plazo_cancelacion_horas:-1 → 422.
   - /tareas/recordatorios sin cabecera → 401; con cita a +24h insertada directamente → enviados:1; repetir → enviados:0.
   - /tareas/purga con cita fin = ahora − 400 días → borradas:1.
   - /tareas/resumen-diario → 200 y 1 telegram.

### FASE 4 — Frontend

1. Descargar https://web-psicologo-demo.vercel.app (Ctrl+S, "página completa"); portar CSS a estilos.css y textos a componentes. Eliminar todos los avisos de prototipo/demo. Conservar el aviso del chat "Asistente automático · no es una persona · no compartas datos de salud".
2. api.ts: una función por endpoint, fetch a VITE_API_URL, throw new Error(detail) si no es 2xx; helpers admin con Authorization desde sessionStorage.
3. ModalReserva.tsx: paso 1 modalidad + tipo de sesión; paso 2 calendario 14 días con inicio_local; paso 3 nombre, email, teléfono opcional, checkbox consentimiento, campo honeypot. Éxito: fecha local, "Gestionar mi cita" (gestion_url), enlace vídeo si online, "Añadir al calendario" (/ics). Error 409 → "Ese horario se acaba de ocupar, elige otro" y recarga huecos.
4. Gestionar.tsx: GET /citas/{token}; si puede_cancelar: Cancelar y Cambiar hora. Si no: texto "Ya no es posible cancelar online" → llama a cancelar y muestra el 403 como "Hemos avisado al psicólogo".
5. Chat.tsx: burbuja flotante, historial en memoria, acciones como botones: abrir_agenda → modal; emergencias → tarjeta con 024 y 112; contacto_urgente → mini-form → /contacto-urgente.
6. Admin.tsx: Login; AgendaSemana (7 columnas, ±semana, cita con nombre/modalidad/estado y acciones); Disponibilidad (tramos por día, PUT); Bloqueos; Ajustes (todos los campos, "Probar Telegram", tarjeta "IA: peticiones restantes hoy").
7. npm run build sin errores; probar a 375 px.

### FASE 5 — Chat IA

1. services/ia.py (6.7) completo. routers/chat.py con el orden de 6.7.
2. tests/test_ia.py:
   - "me quiero morir" → tipo:"crisis", emergencias en acciones, ia.MOCK["llamadas"] == 0.
   - MOCK["respuesta"]="Claro, elige hora. [ABRIR_AGENDA]" → tipo:"ia", respuesta sin [ABRIR_AGENDA], abrir_agenda en acciones.
   - MOCK["respuesta"]=None → tipo:"reglas", respuesta no vacía.
   - 11 mensajes → 422; contenido de 501 chars → 422.
   - 21 peticiones → la 21ª es 429.
   - Con .env real y servidor local: python HARNESS/check.py --con-red hace una petición real (gasta 1 del cupo diario).

### FASE 6 — Operación y despliegue

1. **Render:** New → Web Service → repo → Root Directory backend → Build `pip install -r requirements.txt` → Start `uvicorn app.main:app --host 0.0.0.0 --port $PORT` → Instance Free → Environment: todas las variables de .env con MODO_TEST=false, FRONTEND_URL y CORS_ORIGINS = dominio de Vercel (sin barra final). Copiar la URL a API_URL_PROD en .env local.
2. **Vercel:** Import repo → Root Directory frontend → Environment VITE_API_URL = URL de Render → Deploy.
3. **cron-job.org** (4 tareas, cabecera X-Cron-Secret: <CRON_SECRET>):
   - POST {API}/api/tareas/recordatorios cada hora
   - POST /api/tareas/resumen-diario 08:00 Europe/Madrid
   - POST /api/tareas/purga domingos 04:00
   - GET /api/salud cada 10 min (keep-alive: obligatorio, Render duerme a los 15 min)
4. **Resend:** verificar dominio del cliente y cambiar EMAIL_FROM.
5. python HARNESS/check.py y luego MANUAL_06.md completo.

---

## 9. Errores típicos

| Síntoma | Causa | Arreglo |
|---------|-------|---------|
| can't compare offset-naive and offset-aware datetimes | Lectura naive de Mongo | tz_aware=True en el cliente y a_utc() |
| Huecos desplazados 1–2 h | Datetime construido en UTC | Construir en local con tzinfo=ZoneInfo, convertir con astimezone(utc) |
| Test concurrente da 2×201 | Falta índice o no se captura DuplicateKeyError | crear_indices() en lifespan; try/except en insert_one |
| DuplicateKeyError al reservar un hueco cancelado | Índice no parcial | partialFilterExpression={"estado":"activa"} |
| Rutas admin devuelven 403 sin token | HTTPBearer() con auto_error=True | HTTPBearer(auto_error=False) + 401 manual |
| Event loop is closed en tests | Cliente Motor cacheado entre loops | db.cerrar() al final de la fixture y en shutdown del lifespan |
| Tests de rate limit rompen otros tests | Estado del limiter compartido | app.state.limiter.reset() en la fixture |
| Email no llega | Resend sin dominio verificado | Solo al email de tu cuenta desde onboarding@resend.dev |
| Chat siempre reglas | Cupo gratuito agotado (429) o modelos mal escritos | GET /api/admin/ia/estado; revisar OPENROUTER_MODELOS |
| Vercel 404 en /gestionar/xxx | Sin rewrite | vercel.json |
| CORS bloqueado | CORS_ORIGINS con barra final o dominio distinto | Copiar exacto |
| Primera petición en prod tarda 40 s | Render dormido | Keep-alive de cron-job.org |
