from datetime import datetime

def generar_ics(cita: dict, ajustes: dict) -> str:
    inicio = cita["inicio"]
    fin = cita["fin"]
    token = cita["token"]
    dtstart = inicio.strftime("%Y%m%dT%H%M%SZ")
    dtend = fin.strftime("%Y%m%dT%H%M%SZ")
    dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    gestion_url = f"{cita.get('gestion_url', '')}"
    video = cita.get("video_enlace", "")
    descripcion = f"Gestiona tu cita: {gestion_url}"
    if video:
        descripcion += f"\\nVídeo: {video}"
    return (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Tu Espacio//PSicologia//ES\r\n"
        "CALSCALE:GREGORIAN\r\n"
        "BEGIN:VEVENT\r\n"
        f"UID:{token}@tu-espacio.invalid\r\n"
        f"DTSTAMP:{dtstamp}\r\n"
        f"DTSTART:{dtstart}\r\n"
        f"DTEND:{dtend}\r\n"
        "SUMMARY:Sesión de psicología\r\n"
        f"DESCRIPTION:{descripcion}\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
