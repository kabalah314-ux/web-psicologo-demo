# CHECKLIST_CLIENTE — Tu Espacio

## Cuenta y acceso
- [ ] Cuenta de Render creada (backend)
- [ ] Cuenta de Vercel creada (frontend)
- [ ] Cuenta de MongoDB Atlas configurada
- [ ] Cuenta de OpenRouter configurada
- [ ] Cuenta de Resend configurada (email)
- [ ] Bot de Telegram creado y configurado

## Backend (Render)
- [ ] Servicio web creado en Render
- [ ] Variables de entorno configuradas en Render
- [ ] Servicio desplegado y funcionando
- [ ] Endpoint /api/salud responde 200
- [ ] CORS configurado con la URL del frontend

## Frontend (Vercel)
- [ ] Proyecto importado en Vercel
- [ ] Variable de entorno VITE_API_URL configurada
- [ ] Despliegue automático activado
- [ ] Frontend accesible en la URL de Vercel
- [ ] Rutas profundas funcionan (vercel.json rewrite)

## Dominio y DNS
- [ ] Dominio personalizado configurado (opcional)
- [ ] SSL/HTTPS habilitado

## Funcionalidad verificada
- [ ] Reserva de citas funciona end-to-end
- [ ] Cancelación de citas funciona
- [ ] Chat IA responde correctamente
- [ ] Crisis detecta números de emergencia (024, 112)
- [ ] Notificaciones Telegram funcionan
- [ ] Email de confirmación se envía
- [ ] Panel de administración accesible
- [ ] Tareas programadas (recordatorios, resumen) ejecutan

## Seguridad
- [ ] Contraseña de admin cambiada por defecto
- [ ] JWT_SECRET seguro (32+ caracteres)
- [ ] CRON_SECRET seguro
- [ ] Variables sensibles no expuestas en frontend
- [ ] Rate limiting activado

## Monitoreo
- [ ] Logs de Render revisados
- [ ] Errores de Sentry configurados (opcional)
- [ ] Uptime monitoring configurado (opcional)
