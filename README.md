# VS-1.0.2 Sero - Plataforma de Servidores HTTP con Interfaz Gráfica y Sistema de Autenticación

---

## Índice

- [Descripción general](#descripción-general)  
- [Objetivos y usos](#objetivos-y-usos)  
- [Características principales](#características-principales)  
- [Requisitos técnicos](#requisitos-técnicos)  
- [Estructura del proyecto](#estructura-del-proyecto)  
- [Detalles de implementación](#detalles-de-implementación)  
- [Flujo de usuario](#flujo-de-usuario)  
- [Instrucciones de uso](#instrucciones-de-uso)  
- [Ejemplos de interacción HTTP](#ejemplos-de-interacción-http)  
- [Gestión de usuarios y seguridad](#gestión-de-usuarios-y-seguridad)  
- [Manejo de servidores y puertos](#manejo-de-servidores-y-puertos)  
- [Recomendaciones y posibles mejoras](#recomendaciones-y-posibles-mejoras)  
- [Licencia y contacto](#licencia-y-contacto)

---

## Descripción general

**VS-1.0.2 Sero** es una aplicación de escritorio desarrollada en Python que combina un sistema de servidores HTTP locales con una interfaz gráfica intuitiva construida con Tkinter. Su propósito principal es facilitar la apertura, monitoreo y gestión simultánea de múltiples servidores HTTP en diferentes puertos, con capacidad para recibir datos vía POST.

Adicionalmente, incorpora un sistema robusto de autenticación para controlar el acceso, incluyendo funcionalidades de registro y login, lo que permite administrar quién puede interactuar con la aplicación y visualizar datos.

---

## Objetivos y usos

- Facilitar la recepción y almacenamiento de datos vía HTTP POST en múltiples puertos simultáneos.
- Proveer una interfaz visual para monitorear en tiempo real los datos recibidos por cada servidor.
- Controlar el acceso mediante un sistema de usuarios para entornos donde se requiera autenticación.
- Servir como base para proyectos que requieran recibir datos de dispositivos IoT, aplicaciones cliente, o para propósitos educativos y de prueba.
  
---

## Características principales

| Funcionalidad                        | Descripción                                                                          |
|------------------------------------|--------------------------------------------------------------------------------------|
| Servidores HTTP múltiples           | Soporte para abrir servidores en puertos del 8000 al 8015 simultáneamente             |
| Recepción y guardado de datos POST  | Datos recibidos en cada servidor se guardan en archivos separados (`data_<puerto>.txt`) |
| Visualización en tiempo real        | Actualización dinámica en la GUI del contenido recibido en cada puerto               |
| Sistema de autenticación            | Ventanas modales para registro de nuevos usuarios e inicio de sesión                 |
| Almacenamiento local de usuarios    | Usuarios guardados en formato JSON (`usuarios.json`)                                 |
| Interfaz gráfica amigable            | Uso de Tkinter con pestañas y estilos oscuros para mayor confort visual              |
| Validaciones robustas               | Control de campos vacíos, existencia de usuarios, y validación de contraseñas        |
| Gestión automática de puertos       | Puertos 8000 y 8001 abren servidores automáticamente al iniciar sesión               |
| Mensajes informativos y alertas     | Feedback visual para errores, confirmaciones y estado de servidores                  |

---

## Requisitos técnicos

- Python 3.7 o superior
- Módulos estándar:
  - `http.server`
  - `socketserver`
  - `threading`
  - `tkinter`
  - `queue`
  - `json`
  - `os`

No requiere instalación de paquetes externos, facilitando su uso inmediato en sistemas con Python configurado.

---

## Estructura del proyecto

VS-1.0.2-Sero/
  - main.py # Archivo principal con toda la lógica
  - usuarios.json # Almacenamiento persistente de usuarios (creado en uso)
  - data_8000.txt # Archivos con datos recibidos (uno por puerto)
  - data_8001.txt
  - ...
  - README.md # Documentación detallada del proyecto
  - capturas/ # Imágenes para la documentación y demostración
  - login_register.png
  - interfaz_principal.png
---

## Detalles de implementación

### Servidores HTTP

- Cada servidor se lanza en un hilo independiente usando `threading.Thread`.
- Se usa la clase `HTTPServer` combinada con `BaseHTTPRequestHandler` para manejar solicitudes HTTP.
- El método `do_POST()` recibe datos, los decodifica y guarda en el archivo correspondiente al puerto.
- Se utiliza un sistema de cola (`queue.Queue`) para enviar los datos recibidos a la interfaz gráfica sin bloquear el hilo principal.

### Interfaz gráfica (Tkinter)

- La ventana principal muestra:
  - Lista de puertos abiertos.
  - Botones para abrir y cerrar servidores.
  - Área de texto para visualizar datos recibidos.
  - Mensajes informativos en la parte inferior.
- La ventana modal de login y registro está basada en `ttk.Notebook` para alternar entre pestañas.
- Validaciones en registro e inicio de sesión para asegurar integridad de datos.

### Gestión de usuarios

- Usuarios almacenados en `usuarios.json` con estructura:

```json
[
  {
    "usuario": "nombre_usuario",
    "correo": "correo@ejemplo.com",
    "clave": "contraseña"
  },
  ...
]
