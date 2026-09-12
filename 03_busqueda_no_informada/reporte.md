## Pareja: ZERIND TO CRAIOVA

### 1. ¿BFS encontró el camino con menos carreteras? ¿UCS el de menos km?
- En este caso ambos algorimos tuvieron el mismo resultado: es decir recorriendo 441 KM con una profunidad 4. La diferencia estuvo en el numero de nodos expandidos para BFS 7 y para UCS 10, esto porque BFS explora todos los nodos por niveles en una cola FIFO mientras que UCS toma en cuenta el costo de km recorridos en prioridad de exploración. BFS seria el mas optimo para este caso en particular pues expandio menos nodos. 


### 2. ¿Por qué DFS puede devolver un camino más largo aunque el grafo sea el mismo?
- En este caso como podemos observar en la tabla comparativa, DFS fue el algoritmo que mas KM recorrio (764KM) esto es por sus estrategia de recorrer una rama del arbol de forma profunda hasta encontrar el nodo meta. Para el grafo de ZERIN a CRAIOVA no fue el mas eficiente en terminos de costo en KM. 

### 3. ¿Con qué --limit DLS pasó de cutoff a solución, y cómo se relaciona eso con la profundidad del camino de BFS/IDS?
- El algoritmo limited solo explora a una profundidad limite, en este caso en el limite en 2 tuvimos como resultado cutoff dado que se requeria una profundidad de al menos 4 para alcanzar el nodo meta. Basicamente fue el mismo camino que recorrio BFS y IDS. 

