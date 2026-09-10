from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app import db
from app.routers import publico, chat, admin, tareas

limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.cerrar()
    await db.crear_indices()
    await db.sembrar_defecto()
    yield
    db.cerrar()

app = FastAPI(title="Tu Espacio API", lifespan=lifespan)
app.state.limiter = limiter
if not settings.modo_test:
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(publico.router)
app.include_router(chat.router)
app.include_router(admin.router)
app.include_router(tareas.router)

@app.get("/api/salud")
async def salud():
    return {"ok": True}
