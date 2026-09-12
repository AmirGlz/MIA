# Numpy Vs Keras

## Resumen de ejecución

| Implementación | 2 capas | 4 capas | Efecto observado |
|---|---:|---:|---|
| NumPy manual | ~0.34 | ~0.11 | El error disminuyó más con 4 capas |
| Keras | ~0.222 | ~0.222 | Prácticamente sin mejora |

### 1. ¿Bajar más el error al añadir dos capas, o se estancó / empeoró? ¿Igual en NumPy y en Keras?
- En la implementación de Numpy el error si logro disminuir en 0.23 con cuatro capas. En cambio en Keras el aumento de capas no logro una mejora se mantuvo en 0.222 por lo que podemos concluir que se estanco. 


### 2. ¿Las curvas de la notebook 01 y de Keras se parecen con la misma topología? Si no, ¿qué diferencias de implementación podrían explicarlo (orden de los datos, inicialización, vectorización, etc.)?
- Podemos observar en ambos que el error tiende a disminuir durante el entrenamiento sin embargo hay cambios:
- Con la implementación con Numpy hubieron cambios mas pronunciados, luego estancamientos y en el caso de las 4 capas una disminución significativa del error.
- Con Keras los cambios fueron menos pronunciados hasta llegar a los 0.222.
- La inicialización de los pesos podria explicar el porque de las diferencias, dado que la topologia es practicamente la misma. 

### 3. Con sigmoides apiladas y MSE, ¿tiene sentido que una red más profunda no aprenda mejor en Iris? Relaciónalo con lo que viste en las gráficas.
- No, pues dado que IRIS es un problema pequeño no hay gatantia de que mas capas logren mejor error. 
