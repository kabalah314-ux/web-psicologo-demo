# ESTADO DEL PROYECTO — lo actualiza HARNESS/check.py. Solo edita a mano la sección NOTAS.

FASE_ACTUAL: 5

## Progreso
- [x] Fase 0 — Esqueleto y arnés
- [x] Fase 1 — Motor de agenda
- [x] Fase 2 — API pública + notificaciones
- [x] Fase 3 — API admin + tareas
- [x] Fase 4 — Frontend
- [ ] Fase 5 — Chat IA
- [ ] Fase 6 — Operación y despliegue

## Último check
2026-09-10 23:48 · Fase 4 · COMPLETADA
- PASS · existe frontend/src/api.ts
- PASS · existe frontend/src/estilos.css
- PASS · existe frontend/src/pages/Home.tsx
- PASS · existe frontend/src/pages/Gestionar.tsx
- PASS · existe frontend/src/pages/Admin.tsx
- PASS · existe frontend/src/components/ModalReserva.tsx
- PASS · existe frontend/src/components/Chat.tsx
- PASS · existe frontend/src/components/admin/Login.tsx
- PASS · existe frontend/src/components/admin/AgendaSemana.tsx
- PASS · existe frontend/src/components/admin/Disponibilidad.tsx
- PASS · existe frontend/src/components/admin/Bloqueos.tsx
- PASS · existe frontend/src/components/admin/Ajustes.tsx
- PASS · frontend/src/api.ts contiene '/api/publico/huecos'
- PASS · frontend/src/api.ts contiene '/api/publico/citas'
- PASS · frontend/src/api.ts contiene '/api/chat'
- PASS · frontend/src/api.ts contiene '/api/admin/login'
- PASS · frontend/src/api.ts contiene '/api/admin/ia/estado'
- PASS · frontend/src/api.ts contiene 'VITE_API_URL'
- PASS · frontend/src/components/ModalReserva.tsx contiene 'name="website"'
- PASS · frontend/src/components/ModalReserva.tsx contiene 'consentimiento'
- PASS · frontend/src/components/Chat.tsx contiene '024'
- PASS · frontend/src/components/Chat.tsx contiene '112'
- PASS · frontend/src/components/Chat.tsx contiene 'abrir_agenda'
- PASS · frontend/src/components/Chat.tsx contiene 'contacto_urgente'
- PASS · frontend/src/App.tsx contiene '/gestionar/:token'
- PASS · frontend/src/App.tsx contiene '/admin'
- PASS · 'No tramita citas reales' eliminado de frontend/src
- PASS · 'Agenda de demostración' eliminado de frontend/src
- PASS · 'datos ficticios' eliminado de frontend/src
- PASS · 'localStorage' eliminado de frontend/src
- PASS · `npm run build` en frontend
- PASS · existe frontend/dist/index.html

## NOTAS