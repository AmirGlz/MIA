### 1. Asistente Virtual de Voz

- **Performance:** Buen entendimiento de voz, precisión en respuesta, precisión en realización de tarea, satisfacción de usuario
- **Environment:** Multiples personas, conexión a internet, apps instaladas o conectadas al dispositivo (agenda, alarma, musica, navegador, tienda), conexión a dispositivos inteligentes del hogar.

  - *Observabilidad: parcialmente observable*, pues no todas las tareas ordenadas por voz serán  posibles 

  - *Resultado de acciones: estocastico*, pues dependerá de si por ejemplo una ejecución de tarea sea posible o no. 

  - *Dependencia temporal: secuencial*, por ejemplo una instrucción pudiera ser enciende todas las luces y luego apaga todas las luces. 

  - *Cambio del entorno: dinámico*, pues puede recibir más instrucciones o una instrucción puede ser cancelada 

  - *Estados/Acciones: discreto*, pues los resultados dependen de un conjunto de dispositivos, apps o capacidades del entorno del asistente 

- **Actuators:** buscar información en internet, ejecutar encendido de luces inteligentes, ejecutar apps (música, calendario, recordatorio, mapas) 
- **Sensors:** micrófono, API de conexión a dispositivos inteligentes conectados. 

### 2. Robot Aspirador Doméstico 

- *Performance:* limpieza de una habitación, 
- *Environment:* el mapa de la habitación, obstáculos de la habitación muebles, personas, mascotas

  - *Observabilidad: parcialmente* No tiene conocimiento de otras habitaciones o de objetos que seran obstaculos futuros.

  - *Resulta de acciones: Deterministico*, dependiendo de la acción limpiara o no 

  - *Dependencia temporal: secuencial*, Sigue una ruta, si la limpia esa region de la zona no estara sucia si vuelve a pasar en la misma region ya no necesita limpiar

  - *Cambio del entorno: Dinamico,* obstaculos o personas pueden aparecer.

  - *Estados/Acciones: continuo*, la velocidad y posición de la aspiradora es continua 

- *Actuators:*  Moverse, detectar obstaculo, ejecutar limpieza 

- *Sensors:* camara, sensor de movimiento

### 3.  Sistema de recomendación de streaming

- *Performance:* precisión de recomendación, satisfacción del usuario con la recomendación 
- *Environment:* listas de reproducción del usuario, datos de preferencias del usuario, biblioteca de contenido de la app, el usuario. 

  - *Observabilidad: parcialmente* pues no sabe todos las preferencias del usuario

  - *Resulta de acciones: estocastico*,  pues puede variar dependiendo de los gustos cambiantes del usuario 

  - *Dependencia temporal: secuencial*, pues al sugerir el agente el usuario ciertas recursos puede modificar los gustos del usuario y por tanto las futuras sugerencias 

  - *Cambio del entorno: Dinamico,* el usuario puede ir cambiando de gustos y modificar sugiere biblioteca 

  - *Estados/Acciones: discreto*, hay un número finito de gustos, y las acciones también son finitas

- *Actuators:*  identificar los gustos de usuario, sugerir al usuario, consultar base de datos de películas o música 

- *Sensors:* API de la app para conocer preferencias de usuario, boton favoritos en la app.

### 4.  Vehículo autónomo en ciudad

- *Performance:* precisión de ruta, seguridad, rutas óptimas, confort del usuario 
- *Environment:* tráfico de la ciudad, calles de la ciudad, pasajeros, mapa de la ciudad. 

  - *observababilidad: parcialmente*, no sabe cómo será el tráfico, o qué obstáculos existirán.

  - *Resultado de acciones: estocastico*, irá variando dadas los cambios en el ambiente, por ejemplo si encuentra un obstáculo o no. 

  - *Dependencia: secuencial*, si el auto observa el entorno y ve un obstáculo entonces tomará una decisión y ejecutará otra acción. 

  - *Cambio del entorno: dinámico*, pueden haber cambios, como el clima de la ciudad o una protesta, o un accidente de tránsito.

  - *Estados/Acciones: continuo*, pues la velocidad y distancia son continuas resultado de las acciones del vehículos 


- *Actuators:*  conducir, observar el entorno, cambiar velocidad, consultar mapa, detectar obstáculo 

- *Sensors:* cámara, micrófono y altavoz para comunicación con usuario, API para consultar mapa 


### 5.  Agente de trading algorítmico en bolsa

- *Performance:* toma de decisiones precisa, ganancias para el usuario

- *Environment:* sistema de trading, usuario, noticias en la red. 

  - *Observabilidad: parcial*, no conoce el estado de todos los estados financieros.

  - *Resultado de acciones: estocastico*, la compra de una acción no significa que siempre será buena compra o no. 

  - *Dependencia temporal: secuencial*, ve una oferta, estudia mercado, decide comprar o no. 

  - *Cambio del entorno: dinámico*, los mercados van variando en tiempo real. 

  - *Estados/acciones: discretos*, hay un número finito de acciones: comprar o no, número finito de mercados donde comprar acciones. 
 
- *Actuators:*  comprar acciones, ver estado del mercado, consultar oferta de acciones 

- *Sensors:* API del sistema de trading

### 6.  Sistema de diagnóstico médico asistido por IA 

- *Performance:* buen diagnóstico, buen entendimiento de síntomas, buen análisis de estudios o imágenes clínicas, seguridad del paciente, confort del paciente 
- *Environment:* paciente, estudios clínicos, base de datos de síntomas - enfermedades 
 
  - *Observabilidad: parcial,* no conoce todos los detalles de cada paciente, ni historial clínico.

  - *Resultado de acciones: deterministico,* derivado de análisis y conocimiento del paciente emitirá un diagnóstico 

  - *Dependencia temporal: secuencial,* dependiendo del resultado de cada análisis de síntoma será la siguiente acción o pregunta 

  - *Cambio del entorno: dinámico,* los detalles adicionales en imágenes pueden variar 

  -  *Estados/acciones: discreto,* hay un número finito de combinaciones de síntomas y enfermedades a diagnosticar 

- *Actuators:* escuchar paciente, leer análisis clínicos, revisar imágenes con síntomas observables del paciente. 

- *Sensors:* visión en alta resolución, micrófono

### 6.  Dron de inspección de infraestructura

- *Performance:* recisa revisión de infraestructura, buen análisis de infraestructura, satisfacción de usuario 
- *Environment:* infraestructura a analizar, medio ambiente, obstáculos, personas 

  - *Observabilidad: parcial,* el entorno de la infraestructura no es 100% conocido 

  - *Resultado de acciones: estocastico,* dependerá de las condiciones de infraestructura 

  - *Dependencia temporal: secuencial*

  - *Cambio del entorno: dinámico,* puede moverse obstáculos

  - *Estado/acciones: continuo,* el vuelo del dron, la batería del dron y las dimensiones de lo que el dron puede observar 

- *Actuators:* sobrevolar infraestructura, visualizar infraestructura, analizar infraestructura

- *Sensors:* camara alta resolución, vision infrarroja, sensores de movimiento 


### 6. Agente jugador de ajedrez

- *Performance:* ganar partidas exitosamente, buenas jugadas planteadas
- *Environment:* jugadores (humano, agente) tablero de ajedrez 

  - *Observabilidad: parcial,* no sabe qué jugada hará su contrincante.

  - *Resultado de acciones: deterministico,* cada movimiento será basado en el estado actual del juego 

  - *Dependencia temporal: secuencial,* cada jugada depende del estado actual 

  - *Cambio del entorno: dinámico,* la jugada del contrincante puede variar 

  - *Estado/accion: discreto,* número finito de jugadas 

- *Actuators:*  Moverse pieza, ejecutar jugada, leer tablero

- *Sensors:* camara al resolución