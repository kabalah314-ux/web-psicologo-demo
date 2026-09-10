import base64, logging
import httpx
from app.config import settings

ENVIADOS: list[dict] = []

async def telegram_enviar(texto: str) -> bool:
    if settings.modo_test:
        ENVIADOS.append({"canal": "telegram", "texto": texto})
        return True
    chat_id = settings.TELEGRAM_CHAT_ID
    if not settings.TELEGRAM_BOT_TOKEN or not chat_id:
        return False
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": texto, "parse_mode": "HTML"}
            )
        return r.status_code == 200
    except Exception:
        logging.exception("Error enviando Telegram")
        return False

async def email_enviar(para: str, asunto: str, html: str, ics: str | None = None) -> bool:
    if settings.modo_test:
        ENVIADOS.append({"canal": "email", "para": para, "asunto": asunto, "texto": html})
        return True
    payload = {"from": settings.EMAIL_FROM, "to": [para], "subject": asunto, "html": html}
    if ics:
        payload["attachments"] = [{"filename": "cita.ics", "content": base64.b64encode(ics.encode()).decode()}]
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
                json=payload
            )
        return r.status_code in (200, 201)
    except Exception:
        logging.exception("Error enviando email")
        return False
