# ESTADO DEL PROYECTO — lo actualiza HARNESS/check.py. Solo edita a mano la sección NOTAS.

FASE_ACTUAL: 3

## Progreso
- [x] Fase 0 — Esqueleto y arnés
- [x] Fase 1 — Motor de agenda
- [x] Fase 2 — API pública + notificaciones
- [ ] Fase 3 — API admin + tareas
- [ ] Fase 4 — Frontend
- [ ] Fase 5 — Chat IA
- [ ] Fase 6 — Operación y despliegue

## Último check
2026-09-10 23:04 · Fase 2 · COMPLETADA
- PASS · existe backend/app/schemas.py
- PASS · existe backend/app/services/notify.py
- PASS · existe backend/app/services/citas.py
- PASS · existe backend/app/routers/publico.py
- PASS · existe backend/tests/conftest.py
- PASS · existe backend/tests/test_citas.py
- PASS · backend/app/services/citas.py contiene 'DuplicateKeyError'
- PASS · backend/tests/test_citas.py contiene 'gather'
- PASS · 8 rutas definidas en la API
- PASS · honeypot 400, consentimiento false 422, dias>30 422
- PASS · pytest tests/test_citas.py (≥12 tests, todos PASS)
- PASS · Telegram real al psicólogo [red]

## NOTAS