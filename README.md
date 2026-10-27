# CuentaClara

Aplicación web responsiva para registrar gastos personales de estudiantes. Incluye roles estudiante/administrador, API REST, autenticación JWT, base de datos relacional, integraciones de clima y tipo de cambio, función IA opcional, pruebas y CI.

Repositorio: https://github.com/AndreCN25/Gestion-Gastos-Estudiantiles (rama `feature/cuentaclara`).

## Requisitos

- Python 3.11+
- Git
- (Opcional) Docker

## Instalación y ejecución local

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` y reemplaza `SECRET_KEY` por una cadena aleatoria de 32+ caracteres (puedes generarla con `python -c "import secrets; print(secrets.token_urlsafe(48))"`). Para crear un admin antes del primer arranque, define `ADMIN_EMAIL` y `ADMIN_PASSWORD` (10 a 72 bytes UTF-8). Después ejecuta `uvicorn app.main:app --reload` y abre http://127.0.0.1:8000. No subas `.env`.

## Arquitectura

- `app/main.py`: API FastAPI, rutas, autenticación y validación.
- `app/models.py`: modelos relacionales SQLAlchemy.
- `app/services.py`: integraciones de clima (Open-Meteo), tipo de cambio (Frankfurter) y respuestas generadas con OpenAI cuando hay clave configurada.
- `app/static/`: interfaz adaptable, manifest y service worker.
- `tests/`: pruebas de registro, acceso y operaciones principales.
- SQLite para desarrollo; PostgreSQL configurado por `DATABASE_URL` en producción.

### Modelo de datos

`users (1) -> (N) expenses`. Un usuario tiene correo único, hash de contraseña y rol (`student` o `admin`). Cada gasto pertenece a un usuario, e incluye importe decimal de dos posiciones, moneda admitida, categoría, nota y fecha. Administradores consultan agregados globales; no se exponen hashes.

### Endpoints

| Método | Ruta | Acceso | Propósito |
|---|---|---|---|
| POST | `/api/auth/register` | Público | Crear cuenta estudiante |
| POST | `/api/auth/login` | Público | Iniciar sesión y obtener JWT |
| GET | `/api/me` | Sesión | Perfil y rol |
| GET/POST | `/api/expenses` | Sesión | Listar/crear gastos propios |
| DELETE | `/api/expenses/{id}` | Propietario/admin | Eliminar gasto |
| GET | `/api/summary` | Sesión | Resumen mensual propio |
| GET | `/api/external/weather?city=...` | Sesión | Clima actual aproximado por ciudad |
| GET | `/api/external/exchange?source=MXN&target=USD` | Sesión | Equivalencia de referencia MXN/USD |
| POST | `/api/ai/tips` | Sesión | Recomendaciones basadas en gastos del usuario |
| GET | `/api/admin/summary` | Administrador | Conteos agregados |
| GET | `/health` | Público | Estado de servicio |

## Pruebas

```powershell
python -m pytest -q
```

Las pruebas usan una base SQLite temporal y sustituyen llamadas externas para no depender de red ni claves. GitHub Actions ejecuta las pruebas en cada pull request y push a `main`.

## Variables de entorno

Consulta `.env.example`. `OPENAI_API_KEY` es opcional: si falta, la app entrega una recomendación local por reglas, que no equivale a probar el modelo de lenguaje. Para demostrar IA generativa, configura la clave como secreto. Open-Meteo y Frankfurter no requieren clave. Nunca guardes secretos en el repositorio.

## Despliegue

El archivo `render.yaml` prepara web service y PostgreSQL gratuitos para una demostración escolar. Render duerme el servicio web tras 15 minutos sin tráfico y la base gratuita expira a los 30 días; no guardes allí datos permanentes. Al crear el Blueprint, configura `ADMIN_EMAIL` y `ADMIN_PASSWORD` en el panel; `OPENAI_API_KEY` es opcional. La URL pública queda **pendiente** hasta crear el Blueprint y verificar `/health`.

## Flujo de trabajo del equipo

Trabajen en ramas por función y abran pull requests con revisión cruzada. Prefijos: `[IA]`, `[HUMANO]` o `[MIXTO]`. Los commits de la implementación llevan `[IA]`; recalculen el porcentaje con los cambios humanos reales. Estimación orientativa de esta versión: **90% IA, 0% código humano directo, 10% decisiones/revisión mixta**.

## Documentación de entrega

- `docs/especificacion.md`: especificación previa al desarrollo.
- `docs/bitacoras.md`: índice de dos bitácoras por área. Los prompts literales y reflexiones personales deben completarlos sus autores reales.
- `docs/presentacion.md`: guion de demostración de 10 minutos.

## Seguridad y límites

Passwords se almacenan con bcrypt; tokens JWT expiran; se validan entradas y gastos por propietario. El service worker cachea solo el shell estático. La app no limita intentos de login ni permite revocar sesiones. Para producción hacen falta migraciones, HTTPS y política de privacidad. El clima y el tipo de cambio son informativos; la IA no da asesoría financiera profesional.
