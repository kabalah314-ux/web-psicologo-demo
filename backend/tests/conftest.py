import os
os.environ["MODO_TEST"] = "true"
os.environ["MONGO_DB"] = "tuespacio_test"

import pytest
import httpx
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
    from app.config import settings
    r = await cliente.post("/api/admin/login", json={
        "usuario": settings.ADMIN_USUARIO,
        "password": settings.ADMIN_PASSWORD
    })
    return r.json()["token"]
