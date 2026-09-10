import pytest


@pytest.mark.asyncio
async def test_login_ok(cliente):
    r = await cliente.post("/api/admin/login", json={"usuario": "admin", "password": "E5oze8VhxRDitoYAkR6nqBfOAw-47nw2nJ42KQ7uh6U"})
    assert r.status_code == 200
    assert "token" in r.json()


@pytest.mark.asyncio
async def test_login_mal(cliente):
    r = await cliente.post("/api/admin/login", json={"usuario": "admin", "password": "mala"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_citas_401_sin_token(cliente):
    r = await cliente.get("/api/admin/citas")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_citas_con_token(cliente, token_admin):
    r = await cliente.get("/api/admin/citas", headers={"Authorization": f"Bearer {token_admin}"})
    assert r.status_code == 200
    assert "citas" in r.json()


@pytest.mark.asyncio
async def test_ajustes_get_put(cliente, token_admin):
    h = {"Authorization": f"Bearer {token_admin}"}
    r = await cliente.get("/api/admin/ajustes", headers=h)
    assert r.status_code == 200
    a = r.json()
    a["plazo_cancelacion_horas"] = 48
    r2 = await cliente.put("/api/admin/ajustes", json=a, headers=h)
    assert r2.status_code == 200


@pytest.mark.asyncio
async def test_ajustes_invalidos_422(cliente, token_admin):
    h = {"Authorization": f"Bearer {token_admin}"}
    r = await cliente.get("/api/admin/ajustes", headers=h)
    a = r.json()
    a["plazo_cancelacion_horas"] = -1
    r2 = await cliente.put("/api/admin/ajustes", json=a, headers=h)
    assert r2.status_code == 422


@pytest.mark.asyncio
async def test_bloqueos_crud(cliente, token_admin):
    h = {"Authorization": f"Bearer {token_admin}"}
    r = await cliente.post("/api/admin/bloqueos", json={
        "inicio": "2026-12-01T10:00:00Z",
        "fin": "2026-12-01T12:00:00Z",
        "motivo": "Vacaciones",
    }, headers=h)
    assert r.status_code == 200
    bid = r.json()["_id"]
    r2 = await cliente.get("/api/admin/bloqueos", headers=h)
    assert r2.status_code == 200
    r3 = await cliente.delete(f"/api/admin/bloqueos/{bid}", headers=h)
    assert r3.status_code == 200


@pytest.mark.asyncio
async def test_telegram_test(cliente, token_admin):
    r = await cliente.post("/api/admin/telegram/test", headers={"Authorization": f"Bearer {token_admin}"})
    assert r.status_code == 200
    assert "ok" in r.json()


@pytest.mark.asyncio
async def test_ia_estado(cliente, token_admin):
    r = await cliente.get("/api/admin/ia/estado", headers={"Authorization": f"Bearer {token_admin}"})
    assert r.status_code == 200
    body = r.json()
    assert "is_free_tier" in body
    assert "modelos_disponibles" in body
