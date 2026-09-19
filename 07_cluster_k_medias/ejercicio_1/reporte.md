# K means

### 1. En los datos de Géron, ¿por qué el codo “prefiere” (k = 4) si make_blobs usó 5 centros?
- Dado que 3 centros se encuentran alineados en x = 2.8, en la grafica de k means se observa que algunas de las nubes estan mas compactas para un numero menor de clusters. Entonces el codo analiza cuanto disminuye la inercia al aumentar k, para K=4 la reduccion es grande , mientras que para k=5 es menor. Los blobs cercanos pueden ser tratados por k means como un solo grupo.

### 2. Con tus blobs separados, ¿el codo y la silueta coinciden en el mismo (k)? ¿Ese (k) es 5?
- Si coinciden cuando k = 4, no cuando k = 5, el codo muestra cambios en la su pendiente cuando k=4  con un silhoutte score de 0.69 mientras que para k=5 obtuvimos 0.63. En conclusión Codo -> k=4 y Silueta -> k = 4 

### 3. Si el codo sigue en 4, ¿qué te falta mover (distancia entre centros vs. blob_std)?
- Para nuestro caso convendria alejar mas los centros que aun estan cercanos manteniendo controlada la dispersión ya que si la distancia es pequeña respecto a sus desviaciones, k means no puede distinguir los grupos. En el caso que modificamos, logramos que los cinco grupos sean visiblemente identificables, sin embargo tanto la silueta como el codo favorocen a k=4, por lo que habría que aumentar aun mas la separación de los centros. 