# Bitácora 2 — Interfaz, calidad e integración

**Integrante:** Mariana Isabel Cohuo Pech  
**Fecha de revisión personal:** ____________________  
**Estado:** borrador asistido por IA a partir del código, configuración y pruebas del repositorio. La reflexión personal y las transcripciones reales requieren revisión del integrante.

## Área y objetivo

Esta responsabilidad cubre interfaz móvil, conexión de formularios con la API, experiencia de errores, pruebas, CI y preparación de despliegue. La pantalla permite crear una cuenta, iniciar sesión, registrar y borrar movimientos, mostrar el resumen y solicitar clima, tipo de cambio y recomendaciones. Las pruebas automatizadas usan SQLite temporal y sustituyen servicios externos para que el resultado no dependa de red ni de claves.

## Cinco instrucciones de trabajo para la IA

> Estos enunciados son prompts reproducibles preparados para describir las tareas ejecutadas. No son transcripciones literales de cinco mensajes de una persona. Si la materia exige prompts históricos, el integrante debe sustituirlos por sus prompts reales.

1. “Crea una interfaz móvil en español para que un estudiante registre gastos y consulte su historial con estados vacíos y mensajes de error claros.”
2. “Conecta los formularios de registro, login, creación y eliminación a la API; renderiza el texto del usuario escapado para evitar inyección HTML.”
3. “Integra Open-Meteo y Frankfurter con timeout y errores controlados, y permite simularlos en pruebas automatizadas.”
4. “Añade una recomendación de presupuesto con modelo de lenguaje cuando hay clave y fallback local cuando no la hay; no envíes notas ni correos al modelo.”
5. “Configura GitHub Actions para que cada pull request ejecute las pruebas, y prepara un despliegue de demostración sin secretos en Git.”

## Correcciones concretas observadas

La primera versión del service worker guardaba también respuestas GET de la API. Se limitó la caché a los cuatro recursos estáticos de la aplicación y se añadió un nombre de caché versionado para retirar la caché anterior. También se añadieron pruebas para los extremos de clima y cambio usando respuestas simuladas, además del fallback local de IA, rol admin, interfaz servida y fechas inválidas. El workflow ahora instala todas las dependencias desde `requirements.txt`, que incluye `email-validator`.

El archivo de despliegue inicial proponía una base PostgreSQL de pago. Para no iniciar cargos sin autorización, se cambió a los planes gratuitos de Render. Son adecuados para la demostración escolar, con limitaciones y expiración de la base; no se deben usar para guardar información permanente. El equipo debe revisar su vigencia en la plataforma antes de publicar.

## Dos errores graves de la IA detectados y resolución

1. **Almacenamiento en caché de información de sesión.** Una respuesta privada de gastos podía quedar guardada en caché local. Se corrigió el service worker para almacenar solo archivos de interfaz; la API queda fuera del handler de caché.
2. **Endpoint externo obsoleto.** La prueba real encontró que Frankfurter redirigía el host antiguo y el cliente fallaba con 301. Se cambió a la API vigente de Frankfurter y se verificó una respuesta real. Las pruebas simuladas también ejercitan los endpoints sin llaves ni dependencia de red.

## Decisión de diseño que el integrante debe confirmar

Se optó por permitir la aplicación local y las pruebas sin clave OpenAI, con un fallback explícito por reglas; la llamada al modelo solo ocurre cuando `OPENAI_API_KEY` está configurada. Esta opción mantiene la demo ejecutable sin exponer secretos ni bloquear los flujos. El integrante debe confirmar si está de acuerdo y completar qué otra alternativa evaluó realmente.

## Reflexión personal pendiente

Completar individualmente: ¿qué prueba ejecutaste?, ¿qué resultado viste?, ¿qué comportamiento verificaste en celular?, ¿qué aprendiste al simular APIs en vez de asumir que responden? Añadir aquí cualquier error real que se haya observado al abrir la rama o el despliegue.

**Revisión del integrante (iniciales y fecha):** ____________________
