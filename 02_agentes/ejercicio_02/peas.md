### 1. Asistente Virtual de Voz

- **Performance:** Buen entendimiento de voz, precisión en respuesta, precisión en realización de tarea, satisfacción de usuario
- **Environment:** Multiples personas, conexión a internet, apps instaladas o conectadas al dispositivo (agenda, alarma, musica, navegador, tienda), conexión a dispositivos inteligentes del hogar.
*Observabilidad: parcialmente observable*, pues no todas las tareas ordenadas por voz serán  posibles 
*Resultado de acciones: estocastico*, pues dependerá de si por ejemplo una ejecución de tarea sea posible o no. 
*Dependencia temporal: secuencial*, por ejemplo una instrucción pudiera ser enciende todas las luces y luego apaga todas las luces. 
*Cambio del entorno: dinámico*, pues puede recibir más instrucciones o una instrucción puede ser cancelada 
*Estados/Acciones: discreto*, pues los resultados dependen de un conjunto de dispositivos, apps o capacidades del entorno del asistente 

- **Actuators:** buscar información en internet, ejecutar encendido de luces inteligentes, ejecutar apps (música, calendario, recordatorio, mapas) 
- **Sensors:** micrófono, API de conexión a dispositivos inteligentes conectados. 