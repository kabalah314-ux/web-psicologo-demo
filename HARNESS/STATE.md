# ESTADO DEL PROYECTO — lo actualiza HARNESS/check.py. Solo edita a mano la sección NOTAS.

FASE_ACTUAL: 4

## Progreso
- [x] Fase 0 — Esqueleto y arnés
- [x] Fase 1 — Motor de agenda
- [x] Fase 2 — API pública + notificaciones
- [x] Fase 3 — API admin + tareas
- [ ] Fase 4 — Frontend
- [ ] Fase 5 — Chat IA
- [ ] Fase 6 — Operación y despliegue

## Último check
2026-09-10 23:43 · Fase 3 · COMPLETADA
- PASS · existe backend/app/services/security.py
- PASS · existe backend/app/routers/admin.py
- PASS · existe backend/app/routers/tareas.py
- PASS · existe backend/tests/test_admin.py
- PASS · backend/app/services/security.py contiene 'auto_error=False'
- PASS · 15 rutas definidas en la API
- PASS · todas las rutas admin (salvo login) y tareas → 401 sin token
- PASS · PUT /ajustes inválido → 422 y GET /ia/estado → 200
- PASS · pytest tests/test_admin.py (≥9 tests, todos PASS)

## NOTAS