# ESTADO DEL PROYECTO — lo actualiza HARNESS/check.py. Solo edita a mano la sección NOTAS.

FASE_ACTUAL: 6

## Progreso
- [x] Fase 0 — Esqueleto y arnés
- [x] Fase 1 — Motor de agenda
- [x] Fase 2 — API pública + notificaciones
- [x] Fase 3 — API admin + tareas
- [x] Fase 4 — Frontend
- [x] Fase 5 — Chat IA
- [ ] Fase 6 — Operación y despliegue

## Último check
2026-09-11 10:05 · Fase 6 · EN CURSO
- FAIL · API_URL_PROD y FRONTEND_URL definidos (https) -> en backend/.env deben ser https://…: API_URL_PROD, FRONTEND_URL
- FAIL · prod GET /api/salud -> excepción UnsupportedProtocol: Request URL is missing an 'http://' or 'https://' protocol.
- FAIL · prod GET /api/publico/config -> excepción UnsupportedProtocol: Request URL is missing an 'http://' or 'https://' protocol.
- FAIL · prod tareas sin secreto → 401 -> excepción UnsupportedProtocol: Request URL is missing an 'http://' or 'https://' protocol.
- FAIL · prod tareas con secreto → 200 -> excepción UnsupportedProtocol: Request URL is missing an 'http://' or 'https://' protocol.
- PASS · prod frontend 200
- PASS · prod ruta profunda /gestionar/x → 200 (rewrite)
- FAIL · prod CORS permite el frontend -> excepción UnsupportedProtocol: Request URL is missing an 'http://' or 'https://' protocol.
- PASS · CHECKLIST_CLIENTE.md ≥ 15 casillas

## NOTAS