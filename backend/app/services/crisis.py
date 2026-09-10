import unicodedata, re
from zoneinfo import ZoneInfo

PATRONES = [
    "suicid", "quitarme la vida", "no quiero vivir", "hacerme daño",
    "acabar con todo", "matarme", "morirme", "me quiero morir",
    "autolesion", "no aguanto mas", "no puedo mas", "sobredosis"
]

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
