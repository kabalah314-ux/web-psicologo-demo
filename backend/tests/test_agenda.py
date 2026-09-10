import pytest
from datetime import datetime, date, timedelta, timezone
from app.services.agenda import calcular_huecos, solapa


AJUSTES = {
    "zona_horaria": "Europe/Madrid",
    "duracion_min": 50,
    "buffer_min": 10,
    "antelacion_min_horas": 12,
}

REGLAS = [
    {"dia_semana": 0, "inicio": "09:00", "fin": "14:00", "modalidades": ["online", "presencial"]},
    {"dia_semana": 0, "inicio": "16:00", "fin": "20:00", "modalidades": ["online", "presencial"]},
    {"dia_semana": 1, "inicio": "09:00", "fin": "14:00", "modalidades": ["online", "presencial"]},
    {"dia_semana": 1, "inicio": "16:00", "fin": "20:00", "modalidades": ["online", "presencial"]},
    {"dia_semana": 2, "inicio": "09:00", "fin": "14:00", "modalidades": ["online", "presencial"]},
    {"dia_semana": 2, "inicio": "16:00", "fin": "20:00", "modalidades": ["online", "presencial"]},
    {"dia_semana": 3, "inicio": "09:00", "fin": "14:00", "modalidades": ["online", "presencial"]},
    {"dia_semana": 3, "inicio": "16:00", "fin": "20:00", "modalidades": ["online", "presencial"]},
    {"dia_semana": 4, "inicio": "09:00", "fin": "14:00", "modalidades": ["online", "presencial"]},
    {"dia_semana": 4, "inicio": "16:00", "fin": "20:00", "modalidades": ["online", "presencial"]},
]


def test_huecos_lunes_normal():
    ahora = datetime(2026, 4, 1, tzinfo=timezone.utc)
    h = calcular_huecos(date(2026, 5, 4), "online", AJUSTES, REGLAS, [], [], ahora)
    locales = [x["inicio_local"][-5:] for x in h]
    assert len(locales) == 9
    assert locales == ["09:00", "10:00", "11:00", "12:00", "13:00", "16:00", "17:00", "18:00", "19:00"]
    assert h[0]["inicio"] == datetime(2026, 5, 4, 7, 0, tzinfo=timezone.utc)


def test_huecos_con_cita_activa():
    ahora = datetime(2026, 4, 1, tzinfo=timezone.utc)
    cita = {"inicio": datetime(2026, 5, 4, 8, 0, tzinfo=timezone.utc),
            "fin": datetime(2026, 5, 4, 8, 50, tzinfo=timezone.utc)}
    h = calcular_huecos(date(2026, 5, 4), "online", AJUSTES, REGLAS, [], [cita], ahora)
    assert len(h) == 8
    for hueco in h:
        assert not solapa(hueco["inicio"], hueco["fin"], cita["inicio"], cita["fin"])


def test_huecos_con_bloqueo():
    ahora = datetime(2026, 4, 1, tzinfo=timezone.utc)
    bloqueo = {"inicio": datetime(2026, 5, 4, 7, 0, tzinfo=timezone.utc),
               "fin": datetime(2026, 5, 4, 12, 0, tzinfo=timezone.utc)}
    h = calcular_huecos(date(2026, 5, 4), "online", AJUSTES, REGLAS, [bloqueo], [], ahora)
    assert len(h) == 4


def test_huecos_antelacion_insuficiente():
    ahora = datetime(2026, 5, 4, 6, 0, tzinfo=timezone.utc)
    h = calcular_huecos(date(2026, 5, 4), "online", AJUSTES, REGLAS, [], [], ahora)
    assert len(h) == 0


def test_sabado_sin_huecos():
    ahora = datetime(2026, 4, 1, tzinfo=timezone.utc)
    h = calcular_huecos(date(2026, 5, 9), "online", AJUSTES, REGLAS, [], [], ahora)
    assert len(h) == 0


def test_presencial_con_reglas_solo_online():
    reglas_online = [{"dia_semana": 0, "inicio": "09:00", "fin": "14:00", "modalidades": ["online"]}]
    ahora = datetime(2026, 4, 1, tzinfo=timezone.utc)
    h = calcular_huecos(date(2026, 5, 4), "presencial", AJUSTES, reglas_online, [], [], ahora)
    assert len(h) == 0


def test_dst_primavera():
    ahora = datetime(2026, 3, 1, tzinfo=timezone.utc)
    h = calcular_huecos(date(2026, 3, 30), "online", AJUSTES, REGLAS, [], [], ahora)
    assert len(h) > 0
    assert h[0]["inicio"] == datetime(2026, 3, 30, 7, 0, tzinfo=timezone.utc)


def test_dst_invierno():
    ahora = datetime(2026, 3, 1, tzinfo=timezone.utc)
    h = calcular_huecos(date(2026, 3, 27), "online", AJUSTES, REGLAS, [], [], ahora)
    assert len(h) > 0
    assert h[0]["inicio"] == datetime(2026, 3, 27, 8, 0, tzinfo=timezone.utc)


def test_solapa_adyacentes():
    assert not solapa(
        datetime(2026, 5, 4, 8, 0, tzinfo=timezone.utc),
        datetime(2026, 5, 4, 8, 50, tzinfo=timezone.utc),
        datetime(2026, 5, 4, 8, 50, tzinfo=timezone.utc),
        datetime(2026, 5, 4, 9, 40, tzinfo=timezone.utc),
    )


def test_solapa_contenido():
    assert solapa(
        datetime(2026, 5, 4, 8, 0, tzinfo=timezone.utc),
        datetime(2026, 5, 4, 9, 0, tzinfo=timezone.utc),
        datetime(2026, 5, 4, 8, 30, tzinfo=timezone.utc),
        datetime(2026, 5, 4, 8, 45, tzinfo=timezone.utc),
    )


def test_generar_ics():
    from app.services.ics import generar_ics
    cita = {
        "inicio": datetime(2026, 5, 4, 8, 0, tzinfo=timezone.utc),
        "fin": datetime(2026, 5, 4, 8, 50, tzinfo=timezone.utc),
        "token": "test-token-123",
        "gestion_url": "http://localhost:5173/gestionar/test-token-123",
        "video_enlace": "https://meet.jit.si/TuEspacio-test-token-12",
    }
    ics = generar_ics(cita, AJUSTES)
    assert "BEGIN:VEVENT" in ics
    assert "UID:test-token-123@tu-espacio.invalid" in ics
    assert "BEGIN:VCALENDAR" in ics
