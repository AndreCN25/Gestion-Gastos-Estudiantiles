# CuentaClara

Aplicación web responsiva para que estudiantes registren y consulten gastos personales. Incluye roles estudiante/administrador, API REST, autenticación JWT, base de datos relacional SQLite (PostgreSQL en producción), consulta de clima y tipo de cambio, asistente IA opcional, pruebas y CI.

## Requisitos

- Python 3.11+
- Git
- (Opcional) Docker

## Instalación y ejecución local

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env  # Windows; en macOS/Linux: cp .env.example .env
uvicorn app.main:app --reload
```

Abre http://127.0.0.1:8000. La base SQLite se crea automáticamente. Para crear un administrador, define `ADMIN_EMAIL` y `ADMIN_PASSWORD` antes del primer arranque; sin estas variables se crea únicamente el rol estudiante. Cambia `SECRET_KEY` antes de cualquier despliegue. No subas `.env`.

## Arquitectura

- `app/main.py`: API FastAPI, rutas, autenticación y validación.
- `app/models.py`: modelos relacionales SQLAlchemy.
- `app/services.py`: integraciones de clima (Open-Meteo), tipo de cambio (Frankfurter) y respuestas generadas con OpenAI cuando hay clave configurada.
- `app/static/`: interfaz adaptable, manifest y service worker.
- `tests/`: pruebas de registro, acceso y operaciones principales.
- SQLite para desarrollo; PostgreSQL configurado por `DATABASE_URL` en producción.

### Modelo de datos

`users (1) -> (N) expenses`. Un usuario tiene correo único, hash de contraseña y rol (`student` o `admin`). Cada gasto pertenece a un usuario, e incluye importe positivo, moneda, categoría, nota y fecha. Administradores pueden consultar agregados globales; nunca se exponen hashes.

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
| GET | `/api/external/exchange?from=MXN&to=USD` | Sesión | Tipo de cambio de referencia |
| POST | `/api/ai/tips` | Sesión | Recomendaciones basadas en gastos del usuario |
| GET | `/api/admin/summary` | Administrador | Conteos agregados |
| GET | `/health` | Público | Estado de servicio |

## Pruebas

```bash
pytest -q
```

Las pruebas usan una base SQLite temporal y sustituyen llamadas externas para no depender de red ni claves. GitHub Actions ejecuta las pruebas en cada pull request y push a `main`.

## Variables de entorno

Consulta `.env.example`. `OPENAI_API_KEY` es opcional: si falta, la función IA devuelve sugerencias locales con reglas explícitas. Las APIs de Open-Meteo y Frankfurter no requieren clave. Nunca guardes secretos en el repositorio.

## Despliegue

El archivo `render.yaml` prepara un servicio web y PostgreSQL en Render. Conecta un repositorio GitHub a Render, configura `OPENAI_API_KEY` como secreto (opcional) y despliega. Después añade la URL pública aquí: **Pendiente de despliegue por el equipo**. Este entregable no afirma que exista un repositorio GitHub ni una URL pública activa: se requieren las cuentas y autorización del equipo para publicarlos.

## Flujo de trabajo del equipo

Trabajen en ramas por función y abran pull requests con revisión cruzada. Prefijos sugeridos para cada commit: `[IA]`, `[HUMANO]` o `[MIXTO]`. El repositorio entregado no incluye commits ni PR reales porque no se proporcionó un remoto GitHub. Estimación del código de esta primera versión: **90% IA, 0% humano directo, 10% mixto/revisión de decisiones**. Ajusten el cálculo según sus cambios reales y documenten cada revisión.

## Documentación de entrega

- `docs/especificacion.md`: especificación previa al desarrollo.
- `docs/bitacoras.md`: cuatro bitácoras individuales, con prompts sugeridos y notas transparentes de revisión.
- `docs/presentacion.md`: guion de demostración de 10 minutos.

## Seguridad y límites

Passwords se almacenan con bcrypt; tokens JWT expiran; los datos se filtran por usuario; entradas se validan con Pydantic; CORS queda limitado por configuración; secretos se leen del entorno. El tipo de cambio es informativo, el clima es aproximado y la IA no da asesoría financiera profesional. Antes de producción, revisen dependencias, HTTPS, política de privacidad, límites de uso y configuración del proveedor.
