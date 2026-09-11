# ESTADO DEL PROYECTO — lo actualiza HARNESS/check.py. Solo edita a mano la sección NOTAS.

FASE_ACTUAL: 6

## Progreso
- [x] Fase 0 — Esqueleto y arnés
- [x] Fase 1 — Motor de agenda
- [x] Fase 2 — API pública + notificaciones
- [x] Fase 3 — API admin + tareas
- [x] Fase 4 — Frontend
- [x] Fase 5 — Chat IA
- [x] Fase 6 — Operación y despliegue

## Último check
2026-09-11 14:29 · Fase 6 · COMPLETADA
- PASS · API_URL_PROD y FRONTEND_URL definidos (https)
- PASS · prod GET /api/salud
- PASS · prod GET /api/publico/config
- PASS · prod tareas sin secreto → 401
- PASS · prod tareas con secreto → 200
- PASS · prod frontend 200
- PASS · prod ruta profunda /gestionar/x → 200 (rewrite)
- PASS · prod CORS permite el frontend
- PASS · CHECKLIST_CLIENTE.md ≥ 15 casillas

## NOTAS