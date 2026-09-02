### 1. ¿Qué agentes lograron salir con el oro en tu mapa y cuáles no?
- En el caso particular de esta configuración, ninguno. Tuve que cambiar la configuración que esta documentada como amir_cave_2_4x4.yml y el model based y goal based tuvieron exito

### 2. ¿Por qué el agente de reflejo simple falla (o tiene suerte) en tu diseño?
- En el caso particular de esta configuración, dado que un pit esta en la casilla 2,1 y hay otro pit en la casilla 1,3 el agente inicialmente detecta brisa, por lo que si la regla es que hay brisa cercana entonces girara hasta encontrar un camino seguro.Caso que es incierto puesto que en la casilla 1,2 tambien hay brisa por el pit que esta en la casilla 1,3 por lo que en conclusión el agente se cicla.

### 3. ¿Cómo cambia el resultado del agente basado en modelo si acercas o alejas un pit de la casilla inicial?
- Para esta configuración el agente queda ciclado, alejando uno de los pit, el 1,3 a la posición 1,4  y el pit de la posicion 2,1 a las 3,1, no hay tal ciclo y el agente puede resolver el problema con 33 pasos.


