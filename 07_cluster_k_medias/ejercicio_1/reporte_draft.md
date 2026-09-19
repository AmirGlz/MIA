Resultado: después de modificar los centros se lograron distinguir visualmente los cinco blobs. Sin embargo, tanto el método del codo como el coeficiente de silueta continuaron favoreciendo \(k=4\). La silueta alcanzó aproximadamente 0.69 para \(k=4\), frente a aproximadamente 0.63 para \(k=5\). Esto indica que la separación visual mejoró, pero todavía sería necesario aumentar la distancia relativa entre algunos centros para que cinco clusters resulten más claramente favorecidos por ambos criterios.

Cambio 1: distancia entre centros

Los tres blobs izquierdos dejaron de compartir la misma coordenada \(x\).

Eso fue lo más importante.

Cambio 2: desviaciones

También hicimos más uniformes sus dispersiones.

Curiosamente, los tres blobs originales tenían:

$$ \sigma=0.1 $$

y nosotros usamos:

$$ \sigma=0.25 $$

Así que no hicimos las nubes más pequeñas. Algunas incluso quedaron más dispersas.

Eso hace especialmente interesante el resultado.

20. ¿Funcionó nuestro cambio?

Depende de qué entendamos por "funcionó".

Visualmente: sí.

La tarea pedía:

que los cinco grupos se vean separados a ojo.

Y tu scatter modificado muestra claramente cinco nubes. Ese criterio se cumple.

Para el método del codo: no llegó a \(k=5\).

Siguió:

$$ \boxed{k=4} $$
Para silueta: tampoco.

Obtuviste:

$$ \boxed{k=4} $$

con aproximadamente:

$$ S(4)=0.69 $$

frente a:

$$ S(5)=0.63 $$

Por eso el experimento produjo una conclusión bastante útil:

Separación visual y selección matemática del número de clusters no son exactamente lo mismo.

21. ¿Por qué todavía puede preferir 4?

Porque K-Means no piensa:

"Veo cinco montoncitos."

Su criterio es exclusivamente geométrico:

$$ \min J $$

y la silueta analiza cohesión/separación.

Si al usar cuatro centroides puede representar los datos de manera bastante compacta, introducir un quinto puede no producir una mejora suficientemente importante.

Por eso el ejercicio pregunta explícitamente qué habría que hacer si el codo continúa en 4.

En nuestro caso, como ya tenemos desviaciones relativamente pequeñas:

$$ \sigma=0.25-0.30 $$

una siguiente prueba razonable sería aumentar todavía más la distancia entre algunos centros.

Pero para tu entrega actual no necesitas hacerlo: el resultado de que siga en cuatro forma parte del análisis que la tarea permite.


20. ¿Funcionó nuestro cambio?

Depende de qué entendamos por "funcionó".

Visualmente: sí.

La tarea pedía:

que los cinco grupos se vean separados a ojo.

Y tu scatter modificado muestra claramente cinco nubes. Ese criterio se cumple.

Para el método del codo: no llegó a \(k=5\).

Siguió:

$$ \boxed{k=4} $$
Para silueta: tampoco.

Obtuviste:

$$ \boxed{k=4} $$

con aproximadamente:

$$ S(4)=0.69 $$

frente a:

$$ S(5)=0.63 $$

Por eso el experimento produjo una conclusión bastante útil:

Separación visual y selección matemática del número de clusters no son exactamente lo mismo.

21. ¿Por qué todavía puede preferir 4?

Porque K-Means no piensa:

"Veo cinco montoncitos."

Su criterio es exclusivamente geométrico:

$$ \min J $$

y la silueta analiza cohesión/separación.

Si al usar cuatro centroides puede representar los datos de manera bastante compacta, introducir un quinto puede no producir una mejora suficientemente importante.

Por eso el ejercicio pregunta explícitamente qué habría que hacer si el codo continúa en 4.

En nuestro caso, como ya tenemos desviaciones relativamente pequeñas:

$$ \sigma=0.25-0.30 $$

una siguiente prueba razonable sería aumentar todavía más la distancia entre algunos centros.

Pero para tu entrega actual no necesitas hacerlo: el resultado de que siga en cuatro forma parte del análisis que la tarea permite.

                DATOS SIN ETIQUETAS
                       │
                       ▼
                 ┌──────────┐
                 │ K-MEANS  │
                 └────┬─────┘
                      │
              Elegimos un k
                      │
          ┌───────────┴──────────┐
          ▼                      ▼
    asignar puntos         mover centroides
          │                      │
          └───────────┬──────────┘
                      │
                    repetir
                      │
                      ▼
                  clusters
                      │
             ┌────────┴────────┐
             ▼                 ▼
          INERCIA           SILUETA
             │                 │
             ▼                 ▼
           CODO          cohesión/separación
             └────────┬────────┘
                      ▼
              ¿qué k parece mejor?


                DATOS SIN ETIQUETAS
                       │
                       ▼
                 ┌──────────┐
                 │ K-MEANS  │
                 └────┬─────┘
                      │
              Elegimos un k
                      │
          ┌───────────┴──────────┐
          ▼                      ▼
    asignar puntos         mover centroides
          │                      │
          └───────────┬──────────┘
                      │
                    repetir
                      │
                      ▼
                  clusters
                      │
             ┌────────┴────────┐
             ▼                 ▼
          INERCIA           SILUETA
             │                 │
             ▼                 ▼
           CODO          cohesión/separación
             └────────┬────────┘
                      ▼
              ¿qué k parece mejor?


Esa última conclusión es probablemente el fundamento conceptual más importante de toda la tarea: en clustering no supervisado, el número de grupos con el que se generaron artificialmente los datos no constituye una "respuesta conocida" para K-Means. Los métodos de codo y silueta evalúan la estructura geométrica resultante, y pueden concluir que otra partición representa mejor esos datos según sus respectivos criterios.