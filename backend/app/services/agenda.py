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
            ini = t.astimezone(timezone.utc)
            fin = (t + dur).astimezone(timezone.utc)
            libre = ini >= minimo \
                and not any(solapa(ini, fin, b["inicio"], b["fin"]) for b in bloqueos) \
                and not any(solapa(ini, fin, c["inicio"], c["fin"]) for c in citas_activas)
            if libre:
                huecos.append({"inicio": ini, "fin": fin, "inicio_local": t.strftime("%Y-%m-%dT%H:%M")})
            t += paso
    return sorted(huecos, key=lambda h: h["inicio"])
