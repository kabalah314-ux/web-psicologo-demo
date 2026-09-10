# Comprobaciones manuales — Fase 2

- [ ] Con MODO_TEST=false y servidor local: en /docs, POST /api/publico/citas con un hueco real → 201. Te llega el Telegram y el email (a tu propio correo).
- [ ] Repite el mismo POST → 409.
- [ ] Abre el enlace del email → aún no hay front, pero copia el token y prueba GET /api/publico/citas/{token}/ics → descarga un .ics que se abre en tu calendario.