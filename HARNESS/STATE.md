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
2026-09-10 23:50 · Fase 5 · COMPLETADA
- PASS · existe backend/app/services/ia.py
- PASS · existe backend/app/routers/chat.py
- PASS · existe backend/tests/test_ia.py
- PASS · backend/app/services/ia.py contiene 'openrouter.ai/api/v1/chat/completions'
- PASS · backend/app/services/ia.py contiene 'openrouter.ai/api/v1/key'
- PASS · backend/app/routers/chat.py contiene 'detectar_crisis'
- PASS · 1 rutas definidas en la API
- PASS · crisis → tipo crisis, 024, y la IA NO se llama
- PASS · [ABRIR_AGENDA] se convierte en acción
- PASS · pytest tests/test_ia.py (≥5 tests, todos PASS)
- PASS · petición real a OpenRouter (gasta 1 del cupo) [red]

## NOTAS