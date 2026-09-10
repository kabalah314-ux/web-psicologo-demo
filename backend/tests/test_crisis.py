import pytest
from datetime import datetime, timezone
from app.services.crisis import detectar_crisis, en_horario_laboral


AJUSTES = {
    "zona_horaria": "Europe/Madrid",
    "horario_laboral": {"dias": [0, 1, 2, 3, 4], "inicio": "09:00", "fin": "20:00"},
}


def test_crisis_me_quiero_morir():
    assert detectar_crisis("me quiero morir") is True


def test_no_crisis_reservar():
    assert detectar_crisis("quiero reservar una cita") is False


def test_crisis_suicidio_mayusculas():
    assert detectar_crisis("SUICIDIO") is True


def test_crisis_no_aguanto():
    assert detectar_crisis("No aguanto más") is True


def test_crisis_matarme():
    assert detectar_crisis("quiero matarme") is True


def test_crisis_autolesion():
    assert detectar_crisis("autolesión") is True


def test_en_horario_laboral():
    martes_10h = datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc)
    assert en_horario_laboral(martes_10h, AJUSTES) is True


def test_fuera_horario_domingo():
    domingo = datetime(2026, 5, 10, 8, 0, tzinfo=timezone.utc)
    assert en_horario_laboral(domingo, AJUSTES) is False


def test_fuera_horario_noche():
    martes_20h = datetime(2026, 5, 5, 18, 0, tzinfo=timezone.utc)
    assert en_horario_laboral(martes_20h, AJUSTES) is False
