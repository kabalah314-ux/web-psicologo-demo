import secrets
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

bearer = HTTPBearer(auto_error=False)

def login(usuario: str, password: str) -> bool:
    return secrets.compare_digest(usuario, settings.ADMIN_USUARIO) and secrets.compare_digest(password, settings.ADMIN_PASSWORD)

def crear_jwt() -> str:
    return jwt.encode(
        {"sub": "admin", "exp": datetime.now(timezone.utc) + timedelta(hours=12)},
        settings.JWT_SECRET,
        algorithm="HS256"
    )

async def admin_requerido(cred: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if cred is None:
        raise HTTPException(401, "No autenticado")
    try:
        jwt.decode(cred.credentials, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Token inválido o caducado")

async def cron_requerido(x_cron_secret: str | None = None):
    from fastapi import Header
    # This is a dependency, used via Depends
    pass
