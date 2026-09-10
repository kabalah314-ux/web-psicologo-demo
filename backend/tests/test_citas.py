import os
import pytest
import asyncio
from datetime import datetime, timedelta, timezone

os.environ["MODO_TEST"] = "true"
os.environ["MONGO_DB"] = "tuespacio_test"

from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager
from app.main import app
from app import db
from app.services import notify


@pytest.fixture(autouse=True)
async def setup():
    async with LifespanManager(app):
        d = db.get_db()
        for col in ("citas", "bloqueos", "disponibilidad", "ajustes"):
            await d[col].delete_many({})
        await db.sembrar_defecto()
        notify.ENVIADOS.clear()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c
    db.cerrar()


async def primer_hueco(cliente, modalidad="online"):
    desde = (datetime.now(timezone.utc) + timedelta(days=2)).strftime("%Y-%m-%d")
    r = await cliente.get("/api/publico/huecos", params={"modalidad": modalidad, "desde": desde, "dias": 14})
    huecos = r.json()["huecos"]
    assert len(huecos) >= 1, "No hay huecos disponibles"
    return huecos[0]


async def cita_test(cliente):
    hueco = await primer_hueco(cliente)
    r = await cliente.post("/api/publico/citas", json={
        "inicio": hueco["inicio"],
        "modalidad": "online",
        "tipo_sesion": "primera",
        "nombre": "Persona Test",
        "email": "test@test.com",
        "consentimiento": True,
        "website": ""
    })
    assert r.status_code == 201
    return r.json(), hueco


@pytest.mark.asyncio
async def test_huecos_devuelve_z(setup):
    cliente = setup
    hueco = await primer_hueco(cliente)
    assert hueco["inicio"].endswith("Z")


@pytest.mark.asyncio
async def test_reservar_ok(setup):
    cliente = setup
    data, _ = await cita_test(cliente)
    assert "/gestionar/" in data["gestion_url"]
    emails = [e for e in notify.ENVIADOS if e["canal"] == "email"]
    telegs = [e for e in notify.ENVIADOS if e["canal"] == "telegram"]
    assert len(emails) >= 1
    assert len(telegs) >= 1


@pytest.mark.asyncio
async def test_mismo_hueco_doble_reserva(setup):
    cliente = setup
    data, hueco = await cita_test(cliente)
    r2 = await cliente.post("/api/publico/citas", json={
        "inicio": hueco["inicio"],
        "modalidad": "online",
        "tipo_sesion": "primera",
        "nombre": "Otra Persona",
        "email": "otra@test.com",
        "consentimiento": True,
        "website": ""
    })
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_concurrencia(setup):
    cliente = setup
    hueco = await primer_hueco(cliente)
    payload = {
        "inicio": hueco["inicio"],
        "modalidad": "online",
        "tipo_sesion": "primera",
        "nombre": "Concurrente",
        "email": "conc@test.com",
        "consentimiento": True,
        "website": ""
    }
    r1, r2 = await asyncio.gather(
        cliente.post("/api/publico/citas", json=payload),
        cliente.post("/api/publico/citas", json={**payload, "email": "conc2@test.com"})
    )
    codes = {r1.status_code, r2.status_code}
    assert codes == {201, 409}


@pytest.mark.asyncio
async def test_honeypot_400(setup):
    cliente = setup
    hueco = await primer_hueco(cliente)
    r = await cliente.post("/api/publico/citas", json={
        "inicio": hueco["inicio"],
        "modalidad": "online",
        "tipo_sesion": "primera",
        "nombre": "Bot",
        "email": "bot@test.com",
        "consentimiento": True,
        "website": "spam"
    })
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_consentimiento_false_422(setup):
    cliente = setup
    hueco = await primer_hueco(cliente)
    r = await cliente.post("/api/publico/citas", json={
        "inicio": hueco["inicio"],
        "modalidad": "online",
        "tipo_sesion": "primera",
        "nombre": "Sin Consent",
        "email": "sin@test.com",
        "consentimiento": False,
        "website": ""
    })
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_email_invalido_422(setup):
    cliente = setup
    hueco = await primer_hueco(cliente)
    r = await cliente.post("/api/publico/citas", json={
        "inicio": hueco["inicio"],
        "modalidad": "online",
        "tipo_sesion": "primera",
        "nombre": "Mal Email",
        "email": "no-es-email",
        "consentimiento": True,
        "website": ""
    })
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_dias_31_422(setup):
    cliente = setup
    desde = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    r = await cliente.get("/api/publico/huecos", params={"modalidad": "online", "desde": desde, "dias": 31})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_consultar_cita_puede_cancelar(setup):
    cliente = setup
    data, _ = await cita_test(cliente)
    token = data["gestion_url"].split("/")[-1]
    r = await cliente.get(f"/api/publico/citas/{token}")
    assert r.status_code == 200
    assert r.json()["puede_cancelar"] is True


@pytest.mark.asyncio
async def test_cancelar_fuera_plazo(setup):
    cliente = setup
    from app.services.crisis import en_horario_laboral
    from app.services.notify import telegram_enviar
    ahora = datetime.now(timezone.utc)
    token = "token-fuera-plazo-test"
    cita = {
        "inicio": ahora + timedelta(hours=10),
        "fin": ahora + timedelta(hours=10, minutes=50),
        "modalidad": "online",
        "tipo_sesion": "primera",
        "nombre": "Fuera Plazo",
        "email": "fuera@test.com",
        "telefono": "",
        "estado": "activa",
        "token": token,
        "video_enlace": "",
        "creado_en": ahora,
        "cancelado_en": None,
        "cancelado_por": None,
        "recordatorio_enviado": False,
    }
    await db.get_db()["citas"].insert_one(cita)
    r = await cliente.post(f"/api/publico/citas/{token}/cancelar")
    assert r.status_code == 403
    telegs = [e for e in notify.ENVIADOS if e["canal"] == "telegram"]
    assert any("fuera de plazo" in e["texto"].lower() for e in telegs)


@pytest.mark.asyncio
async def test_cancelar_en_plazo(setup):
    cliente = setup
    data, _ = await cita_test(cliente)
    token = data["gestion_url"].split("/")[-1]
    r = await cliente.post(f"/api/publico/citas/{token}/cancelar")
    assert r.status_code == 200
    desde = (datetime.now(timezone.utc) + timedelta(days=2)).strftime("%Y-%m-%d")
    rh = await cliente.get("/api/publico/huecos", params={"modalidad": "online", "desde": desde, "dias": 14})
    assert len(rh.json()["huecos"]) >= 1
    r2 = await cliente.post(f"/api/publico/citas/{token}/cancelar")
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_reagendar_ok(setup):
    cliente = setup
    data, _ = await cita_test(cliente)
    token = data["gestion_url"].split("/")[-1]
    desde = (datetime.now(timezone.utc) + timedelta(days=3)).strftime("%Y-%m-%d")
    rh = await cliente.get("/api/publico/huecos", params={"modalidad": "online", "desde": desde, "dias": 14})
    nuevos = rh.json()["huecos"]
    assert len(nuevos) >= 1
    r = await cliente.post(f"/api/publico/citas/{token}/reagendar", json={"nuevo_inicio": nuevos[0]["inicio"]})
    assert r.status_code == 200
    assert r.json()["gestion_url"]


@pytest.mark.asyncio
async def test_reagendar_hueco_ocupado(setup):
    cliente = setup
    data1, _ = await cita_test(cliente)
    desde = (datetime.now(timezone.utc) + timedelta(days=3)).strftime("%Y-%m-%d")
    rh = await cliente.get("/api/publico/huecos", params={"modalidad": "online", "desde": desde, "dias": 14})
    nuevos = rh.json()["huecos"]
    assert len(nuevos) >= 2
    token1 = data1["gestion_url"].split("/")[-1]
    payload2 = {
        "inicio": nuevos[0]["inicio"],
        "modalidad": "online",
        "tipo_sesion": "seguimiento",
        "nombre": "Segunda Cita",
        "email": "segunda@test.com",
        "consentimiento": True,
        "website": ""
    }
    r2 = await cliente.post("/api/publico/citas", json=payload2)
    assert r2.status_code == 201
    r3 = await cliente.post(f"/api/publico/citas/{token1}/reagendar", json={"nuevo_inicio": nuevos[0]["inicio"]})
    assert r3.status_code == 409


@pytest.mark.asyncio
async def test_ics(setup):
    cliente = setup
    data, _ = await cita_test(cliente)
    token = data["gestion_url"].split("/")[-1]
    r = await cliente.get(f"/api/publico/citas/{token}/ics")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/calendar")
    assert "BEGIN:VEVENT" in r.text


@pytest.mark.asyncio
async def test_contacto_urgente(setup):
    cliente = setup
    r = await cliente.post("/api/publico/contacto-urgente", json={"nombre": "Urgente", "telefono": "600000000"})
    assert r.status_code == 200
    assert "en_horario" in r.json()
    telegs = [e for e in notify.ENVIADOS if e["canal"] == "telegram"]
    assert len(telegs) >= 1
