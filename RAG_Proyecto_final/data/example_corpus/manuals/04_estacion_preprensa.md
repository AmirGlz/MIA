# Guía de simulación: estación de trabajo de preprensa

> DOCUMENTO SINTÉTICO DE ENTRENAMIENTO. No es un manual HP ni describe una configuración específica de ZBook. Sirve exclusivamente como documento de ejemplo para el prototipo RAG.

## Identificación del incidente

La estación de ejemplo `PC-HP-01` representa un equipo de preprensa que prepara archivos para producción. Una incidencia debe incluir usuario o área, identificador del activo, aplicación afectada, archivo o trabajo (sin incluir datos confidenciales), hora, mensaje exacto y cambios recientes conocidos. Registra si el problema se limita a una aplicación, a una impresora de destino o a toda la estación. La frase “está lento” necesita contexto: tamaño del trabajo, momento de inicio, duración y comparación con el comportamiento normal.

## Cuidado rutinario

El operador puede mantener despejadas las rejillas externas, no bloquear la ventilación y observar avisos del sistema de administración autorizado. Las actualizaciones, análisis de seguridad y respaldos deben seguir la política de TI de la organización. No abras el equipo, cambies memoria o almacenamiento ni instales controladores de sitios no verificados como parte de un diagnóstico improvisado. Los datos de clientes y los archivos de producción se manejan según la política de confidencialidad.

Al comenzar un trabajo crítico, confirma su identificador, versión, destino y resultado de la previsualización conforme al flujo interno. Conserva una copia segura del archivo fuente y documenta cualquier corrección con versión y responsable. No sustituyas una fuente original por un archivo reparado sin registrar el cambio; esa trazabilidad permite separar defecto de archivo, configuración y proceso posterior.

## Diagnóstico seguro

Si una aplicación falla, captura el texto del error y registra la tarea que se realizaba. Comprueba si existe un aviso en el portal de TI antes de volver a ejecutar una operación que pueda duplicar trabajos. Si el sistema pierde conexión, anota si otros servicios siguen disponibles y la hora de la última respuesta. No desactives antivirus, firewall o controles de acceso para probar una hipótesis. Las pruebas de red y restauración corresponden a personal autorizado.

Si el archivo se representa con fuentes, colores o transparencias inesperadas, preserva tanto el original como la versión exportada y la configuración de salida. Compara una copia de referencia y anota la aplicación y su versión. No cambies perfiles globales de color ni reemplaces recursos del sistema sin el procedimiento documentado. Escala diferencias que puedan afectar la producción.

## Registro y recuperación

Una orden clara separa síntomas y diagnóstico confirmado. Ejemplo de observación: “la exportación se detuvo con el mensaje indicado después de abrir el proyecto”. Ejemplo de hipótesis: “posible conflicto de fuente”. Incluye evidencia que permita reproducirlo de forma segura, qué acciones aprobadas se realizaron y el resultado. Si una recuperación usa copia de respaldo, registra su fecha y valida con el usuario dueño del proyecto.

El historial de fallas permite ver recurrencias, como interrupciones tras una actualización o problemas solo en un formato de archivo. La correlación no prueba causalidad. Un plan sugerido por el asistente debe citar los documentos recuperados, marcar inferencias y pedir revisión del equipo de TI antes de aplicar cambios.

## Escalamiento

Escala de inmediato alertas de seguridad, pérdida de datos, acceso no autorizado o fallas que detengan entregas críticas. Conserva registros y evita acciones que borren evidencia. El área de TI define la contención, restauración y liberación del activo. Esta guía es ficticia, no contiene procedimientos de reparación y no reemplaza la documentación oficial del fabricante ni las políticas institucionales.
