# Bitácoras de dirección de IA (borrador para revisión individual)

> Transparencia: estas cuatro bitácoras son borradores generados al construir la primera versión. Los prompts siguientes son prompts propuestos para las tareas de este proyecto, no transcripciones de sesiones independientes ni afirmaciones de que cada integrante los haya usado. Cada persona debe revisar el código, sustituir las observaciones por errores que haya detectado realmente y añadir sus propios prompts antes de entregar.

## 1. Arquitectura / líder técnico

**Prompts clave propuestos (copiados tal cual para esta entrega)**

1. “Diseña una app de gastos estudiantiles con roles estudiante y administrador, define las tablas relacionales y justifica el acceso a datos.”
2. “Propón rutas REST pequeñas para registro, login, gastos, resumen mensual y panel agregado de administrador.”
3. “Revisa el modelo de datos en busca de exposición de información personal entre usuarios.”
4. “Especifica criterios de aceptación verificables para los flujos principales.”
5. “Revisa la estructura del repositorio y documenta decisiones de arquitectura y límites conocidos.”

**Correcciones de esta versión:** el rol admin no es asignable mediante el registro público; se provisiona por variables de entorno. El modelo de resumen conserva monedas separadas para no sumar cantidades incompatibles.

**Dos riesgos graves a revisar:** una clave JWT de desarrollo permitiría falsificar tokens si se desplegara sin reemplazo; por eso se documenta la rotación de `SECRET_KEY` (falta endurecer el arranque para rechazar el valor por defecto en producción). La IA podría recibir datos personales innecesarios; se limita el contexto a importes agregados por categoría.

**Decisión de diseño:** una IA podría sugerir guardar notas completas del usuario para contexto; se eligió no enviarlas al proveedor para reducir exposición.

**Aprendizaje:** verificar siempre límites de acceso, manejo de secretos y sumas por moneda. El equipo debe rellenar una experiencia propia de revisión antes de presentar.

## 2. Backend

**Prompts clave propuestos**

1. “Implementa endpoints FastAPI con SQLAlchemy para registro y login, usando hash de contraseña y tokens JWT con expiración.”
2. “Asegura que las consultas y eliminaciones de gastos se limiten al usuario autenticado.”
3. “Valida importe, moneda, categoría, nota y fecha, y entrega errores HTTP coherentes.”
4. “Integra Open-Meteo y Frankfurter en funciones con timeout y sin exponer claves.”
5. “Añade una función IA que use agregados mínimos y una salida local cuando no existe clave.”

**Correcciones de esta versión:** se agregó comprobación de propiedad al borrar un gasto y conversión de errores externos en 502. La suma agrupa por moneda. Verificar en ejecución que los tipos SQLAlchemy y versiones fijadas son compatibles.

**Dos riesgos graves a revisar:** usar un rol enviado desde el navegador sería escalada de privilegios; el registro asigna `student` en servidor. Consultar gastos sin filtrar `user_id` filtraría datos; la ruta usa la identidad del token.

**Decisión de diseño:** no se envían notas a OpenAI; el sistema resume solo categorías/importes.

**Aprendizaje:** revisar autorización en servidor aunque la interfaz oculte controles; inspeccionar datos salientes de cada proveedor.

## 3. Frontend

**Prompts clave propuestos**

1. “Crea una interfaz móvil primero en español para registrar y entender gastos estudiantiles.”
2. “Conecta formularios de registro e inicio de sesión a la API y muestra errores útiles.”
3. “Renderiza categorías y notas escapando texto para impedir inyección HTML.”
4. “Haz que resumen y movimientos se actualicen después de crear o borrar un gasto.”
5. “Añade controles para clima, cambio y recomendaciones IA, con estados de carga y error.”

**Correcciones de esta versión:** las notas se escapan antes de insertarse en el historial y las rutas privadas usan token Bearer. Validar manualmente en móvil los formularios y teclado numérico.

**Dos riesgos graves a revisar:** insertar una nota directamente con `innerHTML` permite XSS; aquí se escapa texto. Guardar contraseñas en almacenamiento local sería inseguro; solo se conserva el token de acceso y se borra al cerrar sesión (revisar si se prefiere cookie segura HttpOnly para producción).

**Decisión de diseño:** se eligió UI ligera sin framework para que la instalación sea simple y la aplicación sirva desde el mismo backend.

**Aprendizaje:** estados vacíos/errores son parte del flujo y los datos del usuario siempre deben tratarse como texto no confiable.

## 4. Calidad y despliegue

**Prompts clave propuestos**

1. “Escribe pruebas automatizadas para registro, login, gasto, resumen, aislamiento de usuarios y validación.”
2. “Configura GitHub Actions para ejecutar pytest en cada pull request con permisos mínimos.”
3. “Revisa que el repositorio no incluya secretos, archivos de entorno, bases locales ni contraseñas.”
4. “Prepara configuración de despliegue con PostgreSQL y secretos de entorno.”
5. “Documenta cómo instalar, probar, desplegar y verificar la aplicación.”

**Correcciones de esta versión:** CI instala `email-validator`, requerido por `EmailStr`, y las pruebas usan rutas propias. La plataforma despliega una base persistente separada en vez de depender de SQLite efímera.

**Dos errores/riesgos graves a revisar:** pruebas que solo comprueban códigos de estado podrían no proteger privacidad; las pruebas cubren también pertenencia y valor del resumen. Una clave en YAML de CI filtraría acceso; la plantilla no incluye claves y usa secretos de plataforma.

**Decisión de diseño:** se eligió Render con configuración declarativa como ejemplo de despliegue y servicios externos sin clave para no imponer APIs de pago.

**Aprendizaje:** CI verde no demuestra una app segura ni un despliegue público; verificar resultados de ambos y guardar evidencia real.

## Registro de contribución

Estimación inicial orientativa de código: **90% IA, 0% humano escrito directamente, 10% decisiones/revisión mixta**. No hay commits reales en este directorio. Al colaborar, cada integrante debe actualizar esta estimación según el historial `[IA]`, `[HUMANO]`, `[MIXTO]` y dejar constancia verificable de correcciones propias.
