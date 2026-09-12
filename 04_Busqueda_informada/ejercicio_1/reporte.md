## OREADA TO EFORIE

### 1. ¿A* encontró el camino de menos km? ¿Greedy coincidió o se desvió? 
- A* logro llegar en 698km mientras que greedy le tomo 730km. Greedy No coincidio, pues se desvio, en sibiu elegio Fagaras quien tenia mejor heuristica que Rimnicu Vilcea pero mayor costo. De Sibiu a Fagaras el costo fue 99, y hacia Rimnicu Vilcea el costo fue 80 

### 2. ¿Por qué Greedy puede devolver un camino más caro aunque h sea admisible?
- Porque elige el camino que mas parezca corto (basado en la heuristica) sin considerar el costo recorrido, por lo que no garantiza encontrar la meta con el mejor costo.

### 3. En el camino de A*, ¿f tiende a no disminuir a lo largo de la ruta? Relaciónalo con que h sea consistente (en particular si el destino es Bucharest y se usa la tabla AIMA).
-Sí, De Oreada a Eforie estas fueron las f -> 513, 542,580, 581, 595, 634, 676 y 698, por lo que se observa que NO tiende a disminuir. Lo cual significa que h es consistente, cumpliendo la reqla de que h(n)<= c(n,n') + h(n')

