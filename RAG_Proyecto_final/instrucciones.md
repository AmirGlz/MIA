# Instrucciones de uso de la aplicación

Esta guía explica cómo iniciar y usar la interfaz Streamlit del asistente RAG. Streamlit es el único punto de interacción para cargar documentos, hacer preguntas y proponer planes. FastAPI trabaja detrás de la interfaz; `/docs` sirve para consultar la referencia técnica de la API, no para sustituir la UI.

## 1. Requisitos y configuración

- Python 3.10 o posterior.
- Una clave de Google AI Studio con acceso a embeddings y Gemini.
- Las dependencias instaladas desde `requirements.txt`.
- Un archivo `.env` en la raíz con `GOOGLE_API_KEY` configurada.

Si todavía no existe el entorno, desde la raíz del repositorio crea e instala las dependencias:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

Crea `.env` a partir de `.env.example` solo si aún no tienes uno; después agrega tu clave en un editor local. No publiques ni pegues el valor de la clave en terminales compartidas, capturas o Git. FastAPI lee esta configuración al arrancar; reinícialo si modificas `.env`.

En Linux o macOS, puedes crearlo sin sobrescribir un archivo existente con:

```bash
if [ ! -f .env ]; then cp .env.example .env; fi
```

## 2. Iniciar la API y la interfaz

Abre dos terminales en la raíz del proyecto y activa `.venv` en ambas.

En la primera terminal inicia FastAPI:

```bash
uvicorn app.main:app --reload --port 8000
```

En la segunda inicia Streamlit:

```bash
streamlit run ui/streamlit_app.py --server.port 8501
```

Abre <http://localhost:8501>. Mantén ambos procesos ejecutándose mientras usas la aplicación. Para detenerlos, pulsa `Ctrl+C` en cada terminal.

El índice persistente usa `chroma/` por defecto. Reiniciar FastAPI conserva sus documentos. Para empezar con una base vacía, sigue el procedimiento de respaldo y reinicio de [la guía de inicio a fin](corpus_builder/docs/guia_inicio_a_fin.md); no borres la carpeta mientras la API está activa.

## 3. Entender el estado de conexión

La franja superior informa si Streamlit pudo comunicarse con `GET /health` de FastAPI, además del número de documentos y fragmentos indexados por tipo.

- **API conectada:** FastAPI respondió a la solicitud de estado. Esto no valida por sí solo que la clave de Google AI sea aceptada por el proveedor.
- **0 documentos · 0 fragmentos:** todavía no hay archivos ingeridos en Chroma. No es un error; continúa con **Cargar documentos**.
- **Aviso de clave ausente:** `GOOGLE_API_KEY` está vacía o no quedó disponible para FastAPI. Confirma `.env` y vuelve a iniciar la API.

## 4. Módulo «Cargar documentos»

Esta pestaña incorpora conocimiento nuevo al índice persistente.

1. En **Tipo de fuente**, elige **Manual técnico** o **Orden de trabajo PDF**.
2. En **Identificador del equipo**, puedes escribir el ID del equipo si todos los archivos seleccionados corresponden a ese activo. Déjalo vacío para una carga conjunta de varios equipos si no quieres asignar el mismo ID a todos.
3. Selecciona archivos PDF, Markdown (`.md`) o texto (`.txt`). El límite es 75 MB por archivo y los PDF deben tener texto extraíble. No se aceptan hojas Excel. Para seleccionar PDFs comerciales, revisa antes `corpus_builder/input/manual_sources.csv`; no cargues en bloque los archivos auxiliares de la carpeta.
4. Pulsa **Indexar documentos** y espera el resultado. Si hay archivos con error, la interfaz los enumera.

FastAPI extrae el texto y, en los PDF, conserva la página; también guarda una etiqueta de idioma estimado. Luego lo divide en fragmentos de 300 palabras con overlap de 60, Google AI calcula embeddings y Chroma guarda fragmentos, vectores y metadatos. Manuales y órdenes se almacenan en colecciones distintas. Las preguntas detectadas en español también se traducen al inglés para recuperar fuentes inglesas; la traducción solo amplía la búsqueda y no reemplaza el texto original citado. Los embeddings mantienen el mismo modelo y espacio vectorial.

Si cargas otra versión con el mismo nombre de archivo y tipo de fuente, sus fragmentos anteriores se reemplazan. El Excel maestro solo sirve para generar PDFs sintéticos de órdenes desde `corpus_builder`; carga esos PDFs en esta pestaña, no el Excel.

### Asignar equipo a documentos

El ID que escribas al cargar se guarda como metadato para todos los archivos de esa carga. Si varios documentos pertenecen a distintos equipos, cárgalos por grupos separados con el ID correspondiente. Un archivo cargado sin ID seguirá siendo consultable sin filtro de equipo, pero no aparecerá en búsquedas que exijan un `equipment_id`.

## 5. Módulo «Consultar»

Esta pestaña responde preguntas sobre la evidencia que se haya indexado.

1. Escribe una pregunta concreta en **Pregunta**.
2. En **Buscar en**, selecciona **Ambas fuentes**, **Manuales** u **Órdenes de trabajo**.
3. Si quieres limitar la búsqueda a un activo, escribe el ID exacto en **Filtrar por equipo**. Déjalo vacío para buscar en todos los equipos.
4. Ajusta **Fragmentos a recuperar por fuente** entre 1 y 10; el valor inicial es 4. La API consulta las colecciones seleccionadas y combina los resultados antes de devolver como máximo ese número de fragmentos.
5. Pulsa **Consultar**.

La respuesta se redacta en español usando los fragmentos recuperados como evidencia. En **Fuentes recuperadas**, cada cita `[n]` corresponde al fragmento numerado que puede desplegarse para revisar origen, página (si existe), texto y score. El score es una señal de similitud, no una probabilidad de que la respuesta sea correcta.

La búsqueda bilingüe agrega una consulta traducida si el idioma detectado es español; no genera una segunda copia vectorial de los manuales. La traducción requiere una llamada de generación adicional. Si el servicio de generación no está disponible, la búsqueda continúa con la pregunta original.

Si no hay evidencia suficiente, el sistema lo indica y se abstiene. Prueba primero una pregunta respaldada por los documentos, por ejemplo: “¿Qué información conviene registrar cuando una impresora presenta variación de calidad?”. Una pregunta fuera del corpus, como “¿Cuál es la capital de Islandia?”, debe producir una abstención.

## 6. Módulo «Plan de mantenimiento»

El plan se construye cuando lo solicitas: **no se ejecutan tareas sobre los equipos ni se guarda el texto del plan en una base de datos o historial**.

1. Escribe el `equipment_id` exacto en **Identificador del equipo**.
2. Ajusta **Fragmentos por fuente** si deseas cambiar cuánta evidencia se recupera; el valor inicial es 4.
3. Pulsa **Generar plan**.

FastAPI busca por separado historial en la colección de órdenes y procedimientos en la colección de manuales, filtrando ambos conjuntos por ese ID. Gemini redacta una propuesta a partir de la evidencia recuperada. La respuesta presenta las fuentes citadas y un panel **Herramientas utilizadas** con el número de fragmentos encontrados en cada búsqueda.

Para que el plan use tus documentos, asígnales el mismo ID al ingerirlos. Si se cargaron sin ID o con otro ID, la búsqueda filtrada no los encontrará y el plan puede abstenerse. Chroma conserva las fuentes y fragmentos; el plan generado solo aparece en la respuesta de esa solicitud. Revisa cualquier propuesta con el manual oficial y personal responsable antes de tomar decisiones de mantenimiento.

## 7. Preguntas frecuentes y solución de problemas

### ¿Por qué veo «API conectada · 0 documentos · 0 fragmentos (0 manuales, 0 órdenes)»?

Streamlit recibió respuesta de FastAPI, pero las colecciones de Chroma están vacías. Ve a **Cargar documentos** e ingiere manuales o PDFs de órdenes. Si ya habías cargado archivos, confirma que FastAPI usa la misma ruta `CHROMA_PATH` y que no reiniciaste el índice moviendo `chroma/`.

### ¿Por qué veo un aviso de clave de Google AI?

FastAPI no detectó `GOOGLE_API_KEY`. Comprueba que `.env` esté en la raíz y que tenga un valor; no muestres la clave. Reinicia Uvicorn después de editarlo. La conexión API puede aparecer activa aunque la clave no esté configurada.

### La interfaz dice que no puede conectar con la API

Confirma que Uvicorn siga ejecutándose en el puerto 8000 y que `API_BASE_URL` apunte a esa dirección si cambiaste el valor predeterminado (`http://127.0.0.1:8000`). Recarga Streamlit cuando FastAPI vuelva a responder.

### ¿Por qué se rechaza mi archivo o no aparecen fragmentos?

Solo se aceptan PDF, `.md` y `.txt`. Los Excel no se ingieren. Un PDF escaneado sin capa de texto necesita OCR antes de cargarlo. Revisa también el mensaje individual de error de ingesta.

El límite actual es de 75 MB por archivo. Después de indexar, la interfaz informa tamaño, páginas extraídas, idioma estimado y fragmentos creados. Antes de cargar PDFs grandes, ejecuta `corpus_builder/scripts/inspect_manuals.py`; consulta `manual_sources.csv` para excluir accesorios, documentos de otros modelos y fuentes que no sean pertinentes al mantenimiento.

Las preguntas en español también se traducen al inglés para recuperar fragmentos de manuales en inglés. La traducción solo amplía la búsqueda; las citas siguen mostrando el texto original y su página. Si falla la traducción, la búsqueda continúa con la pregunta original.

### ¿Por qué no encuentro citas o el sistema se abstiene?

Confirma que haya documentos en `/health`, quita temporalmente los filtros de fuente y equipo, y pregunta por algo mencionado de forma explícita en el corpus. Para el filtro de equipo, el ID de la consulta debe coincidir con el que se asignó al cargar.

### ¿Dónde se guarda el plan de mantenimiento?

No se guarda. Se genera bajo demanda con fragmentos persistidos de manuales y órdenes; la aplicación no conserva un historial de planes.

## 8. Referencia técnica

Para comprobar estado y conteos abre <http://localhost:8000/health>. La documentación técnica de endpoints está en <http://localhost:8000/docs>. La interacción normal para cargar, consultar y proponer planes se realiza desde Streamlit en <http://localhost:8501>.
