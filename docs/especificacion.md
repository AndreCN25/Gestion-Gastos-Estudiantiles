# Especificación previa al desarrollo - CuentaClara

## Descripción y usuarios

CuentaClara ayuda a estudiantes a registrar gastos personales, revisar totales por categoría y obtener consejos sencillos para administrar su presupuesto. Un administrador puede consultar solo cifras agregadas de uso. Cada cuenta estudiante solo accede a sus propios movimientos. Aplicación web adaptable e instalable como PWA.

## Historias de usuario

1. Como estudiante, quiero crear una cuenta e iniciar sesión para conservar mis datos de forma privada.
2. Como estudiante, quiero registrar importe, fecha, moneda, categoría y nota para llevar un control cotidiano.
3. Como estudiante, quiero consultar mis movimientos y el total del mes para entender mis hábitos.
4. Como estudiante, quiero eliminar un registro propio si lo capturé mal.
5. Como estudiante, quiero recibir sugerencias sobre mis categorías de gasto mediante IA.
6. Como estudiante, quiero consultar el clima de una ciudad y una conversión cambiaria de referencia.
7. Como administrador, quiero consultar conteos agregados de cuentas y gastos sin leer contraseñas ni movimientos privados.
8. Como usuario móvil, quiero usar los flujos principales en una pantalla pequeña.

## Modelo de datos

- `users`: `id` PK, `email` único, `password_hash`, `role`, `created_at`.
- `expenses`: `id` PK, `user_id` FK a `users.id`, `amount` decimal de dos posiciones, `currency`, `category`, `note`, `spent_on`.
- Relación uno a muchos: un usuario tiene cero o más gastos. Al eliminar un usuario, se eliminan sus gastos.

## API REST

| Método | Endpoint | Función |
|---|---|---|
| POST | `/api/auth/register` | Registro de estudiante |
| POST | `/api/auth/login` | Inicio de sesión / JWT |
| GET | `/api/me` | Perfil autenticado |
| GET, POST | `/api/expenses` | Consultar y crear gastos propios |
| DELETE | `/api/expenses/{id}` | Eliminar gasto propio o como admin |
| GET | `/api/summary?month=YYYY-MM` | Agregados personales del mes |
| GET | `/api/external/weather?city=...` | Open-Meteo: geocodificación y clima |
| GET | `/api/external/exchange?from=MXN&to=USD` | Frankfurter: tipo de cambio |
| POST | `/api/ai/tips` | Consejos a partir de agregados propios |
| GET | `/api/admin/summary` | Agregados de la plataforma, solo admin |
| GET | `/health` | Health check |

## Integraciones y herramientas IA

- Open-Meteo (geocodificación y pronóstico actual) y Frankfurter (tipo de cambio); llamadas del servidor con timeout y errores controlados.
- OpenAI Chat Completions, activada solo si se configura `OPENAI_API_KEY`; alternativa local determinista para ejecutar sin clave. Al modelo solo se envían sumas por categoría, no correo ni notas.
- Se propone usar un asistente de código IA para tareas pequeñas por área: arquitectura, API, interfaz y calidad/despliegue. La persona responsable revisa y explica cada cambio. No se inventan resultados de revisión ni de despliegue.

## Seguridad y aceptación

Contraseñas con bcrypt, JWT con vencimiento, roles comprobados en backend, consultas limitadas al propietario, validación de entradas y secretos por entorno. Aceptación: pruebas de registro/login, registro y resumen de gastos, aislamiento entre usuarios y entradas inválidas; CI debe correr al abrir PR. La URL pública y el repositorio son campos por completar al publicarse con cuentas del equipo.
