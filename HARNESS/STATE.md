# ESTADO DEL PROYECTO — lo actualiza HARNESS/check.py. Solo edita a mano la sección NOTAS.

FASE_ACTUAL: 2

## Progreso
- [x] Fase 0 — Esqueleto y arnés
- [x] Fase 1 — Motor de agenda
- [ ] Fase 2 — API pública + notificaciones
- [ ] Fase 3 — API admin + tareas
- [ ] Fase 4 — Frontend
- [ ] Fase 5 — Chat IA
- [ ] Fase 6 — Operación y despliegue

## Último check
2026-09-10 22:58 · Fase 1 · COMPLETADA
- PASS · existe backend/app/services/agenda.py
- PASS · existe backend/app/services/crisis.py
- PASS · existe backend/app/services/ics.py
- PASS · existe backend/app/services/video.py
- PASS · existe backend/tests/test_agenda.py
- PASS · existe backend/tests/test_crisis.py
- PASS · calcular_huecos lunes 2026-05-04 → 9 huecos exactos
- PASS · pytest tests/test_agenda.py tests/test_crisis.py (≥12 tests, todos PASS)
- PASS · índice único parcial citas.inicio (estado=activa)
- PASS · sembrar_defecto idempotente: ajustes + 10 reglas

## NOTAS