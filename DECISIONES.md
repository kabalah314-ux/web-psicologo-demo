# DECISIONES BLOQUEADAS — no se cambian sin autorización escrita del humano

1. Stack: React 18 + TypeScript (Vite) / FastAPI (Python 3.11+) / MongoDB Atlas M0. Prohibido: Next.js, Postgres, SQLite, Prisma, Django, Docker.
2. Hosting: backend en Render (Free), frontend en Vercel, cron externo en cron-job.org.
3. La IA (OpenRouter) NO crea, modifica ni cancela citas. Solo conversa. La lógica de agenda es código determinista con tests.
4. Sin tool-calling. El contexto (huecos, tarifas) se inyecta en el system prompt.
5. Detector de crisis en código, ANTES de la IA. El mensaje detectado nunca se envía a OpenRouter.
6. Sin cuentas de paciente. Gestión por enlace con token secrets.token_urlsafe(32).
7. Un único admin (el psicólogo): usuario/contraseña en variables de entorno + JWT HS256 (PyJWT).
8. Fechas en MongoDB siempre UTC aware. Zona local en ajustes (Europe/Madrid). zoneinfo, nunca pytz.
9. Doble reserva imposible por índice único parcial en MongoDB, no por comprobaciones en Python.
10. Datos mínimos: nombre, email, teléfono opcional. Sin texto libre. El chat no se persiste.
11. Telegram por httpx (POST sendMessage). Email por Resend HTTP. Sin librerías de Telegram ni SMTP.
12. Vídeo: enlace fijo del psicólogo o sala Jitsi aleatoria. Sin OAuth de Google. Sin Google Calendar en v1 (.ics).
13. Tareas programadas: endpoints con cabecera X-Cron-Secret. Sin APScheduler/Celery.
14. Toda la API bajo /api. Auth admin con HTTPBearer(auto_error=False) y 401 manual (nunca 403 por falta de token).
15. Tests: pytest + pytest-asyncio + httpx.AsyncClient(ASGITransport) + asgi-lifespan. Base de datos de test: tuespacio_test.
