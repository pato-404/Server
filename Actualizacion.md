# Historial de Actualizaciones y Próximos Cambios

## VS-1.0.2 Sero

### Estado actual
- Aplicación de escritorio en Tkinter con interfaz moderna y oscura.
- Servidores HTTP multihilo corriendo en puertos seleccionables.
- Registro e inicio de sesión con almacenamiento en JSON.
- Recepción y almacenamiento de datos POST en archivos por puerto.
- Visualización en tiempo real de datos recibidos.
- Control de puertos abiertos y listado en interfaz.

---

## Próximas Actualizaciones Planeadas

### VS-1.1.0 - Mejoras de Seguridad y Funcionalidad de Usuarios
- [ ] Implementar hashing seguro de contraseñas (bcrypt o similar) para almacenamiento en JSON.
- [ ] Añadir recuperación de contraseña vía correo electrónico.
- [ ] Validar formato de correo en el registro.
- [ ] Limitar intentos de inicio de sesión para evitar ataques de fuerza bruta.
- [ ] Añadir opción para cerrar sesión y cambiar usuario sin reiniciar la app.

### VS-1.2.0 - Mejoras en la Gestión de Servidores y Puertos
- [ ] Añadir funcionalidad para cerrar servidores/puertos abiertos desde la interfaz.
- [ ] Mostrar estado detallado de cada servidor (conexiones activas, tiempo de actividad).
- [ ] Permitir configurar respuestas HTTP personalizadas en cada servidor.
- [ ] Añadir logs detallados y exportación de datos recibidos.

### VS-1.3.0 - Mejoras en la Interfaz y Usabilidad
- [ ] Mejorar el diseño visual con temas personalizados y modos claro/oscuro.
- [ ] Añadir soporte multilenguaje para la interfaz.
- [ ] Implementar búsqueda y filtrado de datos recibidos.
- [ ] Añadir notificaciones visuales o sonoras ante nuevos datos entrantes.
- [ ] Mejorar experiencia móvil o remota (posible versión web).

### VS-1.4.0 - Extensiones y Automatización
- [ ] Añadir integración con bases de datos para almacenamiento escalable (SQLite o similar).
- [ ] Añadir opciones para enviar alertas vía correo o mensajes cuando se reciben datos específicos.
- [ ] Soporte para autenticación OAuth o integración con servicios externos.
- [ ] Añadir API REST para controlar servidores y obtener datos desde otras aplicaciones.
- [ ] Añadir soporte para múltiples protocolos HTTP (GET, PUT, DELETE).

---

## Cambios Propuestos en Código Actual

- Refactorizar la gestión de hilos para permitir cierre y reinicio seguro de servidores.
- Separar lógica de UI y lógica de servidor para facilitar mantenimiento.
- Implementar manejo avanzado de errores y validación de datos recibidos.
- Añadir pruebas unitarias y de integración para las funcionalidades principales.
- Mejorar documentación inline y estructura general del proyecto.

---

Si tienes sugerencias o ideas para nuevas funcionalidades, ¡no dudes en comentarlas!

