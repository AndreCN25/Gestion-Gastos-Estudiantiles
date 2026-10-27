# Bitácora 1 — Arquitectura y backend

**Integrante:** Andre Castillo Novelo  
**Fecha de revisión personal:** ____________________  
**Estado:** borrador asistido por IA a partir del código y pruebas del repositorio. No se atribuyen reflexiones ni sesiones a una persona sin que esta las complete.

## Área y objetivo

La responsabilidad de esta bitácora es arquitectura y backend: especificar el modelo de datos, implementar autenticación y autorización por rol, definir la API y revisar que los datos de cada estudiante permanezcan privados. CuentaClara se eligió como registro de gastos estudiantiles con dos roles: `student` y `admin`. La relación central es `users (1) -> (N) expenses`; el registro público siempre asigna el rol estudiante y el admin se provisiona por configuración.

## Cinco instrucciones de trabajo para la IA

> Estos enunciados son prompts reproducibles preparados para describir las tareas ejecutadas. No son transcripciones literales de cinco mensajes de una persona. Si la materia exige prompts históricos, el integrante debe sustituirlos por sus prompts reales.

1. “Diseña el modelo relacional de una app de gastos estudiantiles con usuarios y movimientos; define claves, relaciones y restricciones.”
2. “Implementa registro e inicio de sesión en FastAPI con bcrypt, JWT con expiración y respuestas que nunca revelen el hash de contraseña.”
3. “Revisa cada consulta y mutación de gastos para que un estudiante solo alcance registros propios; restringe el resumen global al rol admin.”
4. “Valida cantidades monetarias, moneda, fecha y texto de entrada; indica qué error HTTP debe devolver cada caso inválido.”
5. “Escribe pruebas de registro, login, propiedad de datos, rol administrador, resumen y entradas inválidas sin depender de servicios externos.”

## Correcciones concretas observadas

En la revisión del código se identificó que los importes se almacenaban como `float`. Para dinero, eso puede introducir errores de representación y redondeo; el modelo y el esquema se cambiaron a decimal con dos posiciones (`Numeric(12,2)` y `Decimal`) y el resumen suma por moneda. También se encontró que el parámetro de mes solo comprobaba su forma (`AAAA-MM`): `2026-99` podía provocar un error interno. Se añadió validación de fecha y una prueba que exige respuesta 422. Estas correcciones se verifican en `app/models.py`, `app/schemas.py`, `app/main.py` y `tests/test_flows.py`.

## Dos errores graves de la IA detectados y resolución

1. **Persistencia monetaria aproximada.** La primera implementación usaba coma flotante para importes. Se reemplazó por decimal de dos posiciones y se extendieron las pruebas para comparar el valor `125.50` exactamente.
2. **Caché de respuestas privadas.** El service worker guardaba cualquier respuesta GET del mismo origen, incluidas `/api/expenses` y `/api/summary`, que contienen datos asociados a una sesión. Se limitó el almacenamiento a la lista cerrada de archivos estáticos del shell y se versionó la caché. La verificación de la suite y la revisión del service worker deben repetirse antes de integrar.

## Decisión de diseño que el integrante debe confirmar

La implementación conserva los totales por moneda y no convierte todo a MXN antes de resumir. Así evita sumar magnitudes incomparables y evita depender de una tasa de cambio que puede cambiar. El registro de esta decisión proviene de la implementación asistida; el integrante debe confirmar que la entiende, agregar su motivo personal y anotar cualquier alternativa que sí haya discutido con el equipo.

## Reflexión personal pendiente

Completar con palabras propias: ¿qué parte de autorización revisaste directamente?, ¿qué salida de la IA no aceptaste sin comprobar?, ¿qué aprendiste sobre revisar lógica financiera y permisos? No copiar una respuesta generada si no refleja la experiencia real del integrante.

**Revisión del integrante (iniciales y fecha):** ____________________
