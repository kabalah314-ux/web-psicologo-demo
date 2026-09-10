import pytest


@pytest.mark.asyncio
async def test_chat_respuesta_basica(cliente):
    from app.services import ia
    ia.MOCK.update(respuesta="Hola, ¿en qué puedo ayudarte?", llamadas=0)
    r = await cliente.post("/api/chat", json={"mensajes": [{"rol": "usuario", "contenido": "hola"}]})
    assert r.status_code == 200
    d = r.json()
    assert d["tipo"] == "ia"
    assert "hola" in d["respuesta"].lower() or "ayudar" in d["respuesta"].lower()


@pytest.mark.asyncio
async def test_crisis_sin_llamar_ia(cliente):
    from app.services import ia
    ia.MOCK.update(respuesta="NO DEBERÍA LLEGAR", llamadas=0)
    r = await cliente.post("/api/chat", json={"mensajes": [{"rol": "usuario", "contenido": "ya no puedo más, me quiero morir"}]})
    d = r.json()
    assert r.status_code == 200
    assert d["tipo"] == "crisis"
    assert "emergencias" in d["acciones"]
    assert "024" in d["respuesta"]
    assert ia.MOCK["llamadas"] == 0


@pytest.mark.asyncio
async def test_agenda_tag_se_convierte_en_accion(cliente):
    from app.services import ia
    ia.MOCK.update(respuesta="Claro, elige la hora que prefieras. [ABRIR_AGENDA]", llamadas=0)
    r = await cliente.post("/api/chat", json={"mensajes": [{"rol": "usuario", "contenido": "quiero reservar"}]})
    d = r.json()
    assert d["tipo"] == "ia"
    assert "[ABRIR_AGENDA]" not in d["respuesta"]
    assert "abrir_agenda" in d["acciones"]


@pytest.mark.asyncio
async def test_reglas_reserva(cliente):
    from app.services import ia
    ia.MOCK.update(respuesta=None, llamadas=0)
    r = await cliente.post("/api/chat", json={"mensajes": [{"rol": "usuario", "contenido": "¿cómo reservo una cita?"}]})
    d = r.json()
    assert d["tipo"] == "reglas"
    assert "abrir_agenda" in d["acciones"]


@pytest.mark.asyncio
async def test_reglas_precio(cliente):
    from app.services import ia
    ia.MOCK.update(respuesta=None, llamadas=0)
    r = await cliente.post("/api/chat", json={"mensajes": [{"rol": "usuario", "contenido": "¿cuánto cuesta?"}]})
    d = r.json()
    assert d["tipo"] == "reglas"
    assert "abrir_agenda" in d["acciones"]


@pytest.mark.asyncio
async def test_reglas_duración(cliente):
    from app.services import ia
    ia.MOCK.update(respuesta=None, llamadas=0)
    r = await cliente.post("/api/chat", json={"mensajes": [{"rol": "usuario", "contenido": "¿cuánto dura una sesión?"}]})
    d = r.json()
    assert d["tipo"] == "reglas"
    assert "50" in d["respuesta"]
