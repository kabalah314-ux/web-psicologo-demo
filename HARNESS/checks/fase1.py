from checks import *

def indice_unico_parcial():
    async def go():
        from app.db import get_db, crear_indices
        await crear_indices(); info = await get_db()["citas"].index_information()
        ok = any(v.get("unique") and v.get("partialFilterExpression", {}).get("estado") == "activa"
                 and list(v["key"]) == [("inicio", 1)] for v in info.values())
        return ok, str(info)
    return corre(go())

def semilla():
    async def go():
        from app.db import get_db, sembrar_defecto
        db = get_db(); await db["ajustes"].delete_many({}); await db["disponibilidad"].delete_many({})
        await sembrar_defecto(); await sembrar_defecto()   # idempotente
        a = await db["ajustes"].find_one({"_id": "ajustes"}); n = await db["disponibilidad"].count_documents({})
        return (a is not None and n == 10 and a.get("zona_horaria") == "Europe/Madrid", f"ajustes={a is not None}, reglas={n}")
    return corre(go())

def huecos_lunes():
    from datetime import datetime, date, timezone
    from app.services.agenda import calcular_huecos
    ajustes = {"zona_horaria": "Europe/Madrid", "duracion_min": 50, "buffer_min": 10, "antelacion_min_horas": 12}
    reglas = [{"dia_semana": 0, "inicio": "09:00", "fin": "14:00", "modalidades": ["online", "presencial"]},
              {"dia_semana": 0, "inicio": "16:00", "fin": "20:00", "modalidades": ["online", "presencial"]}]
    h = calcular_huecos(date(2026, 5, 4), "online", ajustes, reglas, [], [], datetime(2026, 4, 1, tzinfo=timezone.utc))
    locales = [x["inicio_local"][-5:] for x in h]
    return (locales == ["09:00", "10:00", "11:00", "12:00", "13:00", "16:00", "17:00", "18:00", "19:00"]
            and h[0]["inicio"] == datetime(2026, 5, 4, 7, 0, tzinfo=timezone.utc), str(locales))

CRITERIOS = [existe("backend/app/services/agenda.py"), existe("backend/app/services/crisis.py"),
             existe("backend/app/services/ics.py"), existe("backend/app/services/video.py"),
             existe("backend/tests/test_agenda.py"), existe("backend/tests/test_crisis.py"),
             ("calcular_huecos lunes 2026-05-04 → 9 huecos exactos", huecos_lunes),
             pytest_pasa("tests/test_agenda.py", "tests/test_crisis.py", minimo=12),
             ("índice único parcial citas.inicio (estado=activa)", indice_unico_parcial),
             ("sembrar_defecto idempotente: ajustes + 10 reglas", semilla)]