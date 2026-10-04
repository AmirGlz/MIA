# Guía de inicio a fin: reiniciar, cargar y probar el RAG

Esta guía explica cómo crear un índice Chroma limpio de forma reversible, preparar el corpus de ejemplo, cargarlo desde la única interfaz de usuario (Streamlit), comprobar respuestas con citas y validar que el índice persiste al reiniciar FastAPI.

> **Importante:** reiniciar Chroma hace que la aplicación olvide el índice actual mientras se use el índice nuevo. El proceso aquí descrito mueve la carpeta anterior a `/tmp` como respaldo; no la elimina. No subas respaldos ni `.env` a Git.

## 1. Preparar el entorno

Abre una terminal en la raíz del proyecto:

```bash
cd /home/amir/Documents/MIA2026/RAG_Proyecto_final
source .venv/bin/activate
```

En Windows, activa con `.venv\Scripts\activate`. Si aún no instalaste dependencias, hazlo desde la raíz:

```bash
python -m pip install -r requirements.txt
```

Comprueba que `.env` exista sin imprimir su contenido:

```bash
test -f .env && echo ".env encontrado"
```

Abre `.env` en un editor local y confirma que `GOOGLE_API_KEY` tenga un valor. No copies la clave a una terminal compartida, captura, mensaje o repositorio. Los nombres de modelo, chunking y abstención se encuentran en `.env.example`; por defecto son `gemini-embedding-001`, `gemini-3.8-flash`, 300 palabras, overlap 60 y score mínimo 0.35.

Obtén la ruta efectiva de Chroma. La ruta predeterminada es `./chroma`, relativa a la raíz del repositorio; `CHROMA_PATH` en el entorno o `.env` puede cambiarla:

```bash
.venv/bin/python -c 'from app.config import get_settings; print(get_settings().chroma_directory)'
```

En los pasos siguientes la variable `CHROMA_DIR` se calculará desde esa configuración. La API abre esa misma ruta al iniciar.

## 2. Respaldar y reiniciar la base vectorial

No existe un endpoint de borrado. Para empezar con colecciones vacías, primero detén FastAPI en su terminal con `Ctrl+C`. Deja Streamlit cerrado o detenido también para evitar que consulte una API apagada.

Desde una terminal en la raíz, mueve el directorio de Chroma a un respaldo fechado fuera del repositorio:

```bash
CHROMA_DIR="$(.venv/bin/python -c 'from app.config import get_settings; print(get_settings().chroma_directory)')"
BACKUP_DIR="/tmp/rag-chroma-backup-$(date +%Y%m%d-%H%M%S)"
if [ -d "$CHROMA_DIR" ]; then
  mv "$CHROMA_DIR" "$BACKUP_DIR"
  echo "Respaldo Chroma: $BACKUP_DIR"
else
  echo "No existe índice previo en $CHROMA_DIR; FastAPI creará uno nuevo."
fi
```

Guarda la ruta que imprima el comando si movió una base existente. **No uses `rm -rf`**. Al iniciar FastAPI en el paso 4, Chroma creará el directorio y las colecciones vacías. Abre `http://localhost:8000/health` y verifica `index.total_documents` y `index.total_chunks` en cero.

### Restaurar el índice anterior

Si necesitas volver al índice respaldado, detén FastAPI. Mueve el índice nuevo a otro respaldo y devuelve el directorio anterior a la ruta que mostró el primer comando:

```bash
CHROMA_DIR="$(.venv/bin/python -c 'from app.config import get_settings; print(get_settings().chroma_directory)')"
FRESH_DIR="/tmp/rag-chroma-fresh-$(date +%Y%m%d-%H%M%S)"
mv "$CHROMA_DIR" "$FRESH_DIR"
mv "/tmp/rag-chroma-backup-AAAAMMDD-HHMMSS" "$CHROMA_DIR"
```

Reemplaza `AAAAMMDD-HHMMSS` por la fecha y hora exactas del respaldo. Después vuelve a iniciar FastAPI. Conserva los respaldos en `/tmp` solo mientras los necesites; no se incluyen en el repositorio.

## 3. Validar y preparar el corpus

Ejecuta desde la raíz:

```bash
python corpus_builder/scripts/inspect_manuals.py
python corpus_builder/scripts/build_demo_work_orders.py
python corpus_builder/scripts/validate_dataset.py
python corpus_builder/scripts/generate_work_orders.py
python corpus_builder/scripts/validate_example_corpus.py
```

El inspector estima tamaño, páginas y fragmentos de las fuentes aprobadas sin llamar a IA. El constructor recrea las 100 filas sintéticas (25 por equipo); después se valida el Excel, se crea un PDF por fila y se comprueban texto extraíble y distribución. Consulta `manual_sources.csv` antes de elegir PDFs comerciales para carga; excluye archivos auxiliares, folletos o especificaciones que no sean pertinentes al tipo de consulta.

El Excel de `corpus_builder/input/` sirve únicamente para crear órdenes PDF. **No cargues el Excel en Streamlit**: la UI acepta PDF, Markdown y TXT, y los PDFs son los documentos de órdenes que indexa. Usa `manual_sources.csv` para elegir manuales; el PDF IDEAL local es folleto y los documentos Kodak son referencias de interfaz, no manuales de reparación física.

### Selección para trabajar con la cuota gratuita

Google no define un número fijo de archivos que se puedan cargar gratis. Los límites se aplican por proyecto y modelo, y pueden incluir solicitudes por minuto, tokens por minuto y solicitudes por día; consulta los límites efectivos del proyecto en [AI Studio](https://aistudio.google.com/) y la [documentación de límites de Gemini](https://ai.google.dev/gemini-api/docs/rate-limits). El error que vimos en este proyecto reportó **100 solicitudes de embeddings por minuto** para la cuota gratuita. Ese número cuenta solicitudes a la API, no PDFs ni fragmentos. La carga manda hasta 50 fragmentos por solicitud de embeddings.

Para pruebas con un manual comercial, elige **`data/example_corpus/manuals/pdf_11954803_en-US-1.pdf`**, guía de usuario de la HP LaserJet Enterprise MFP 5602. Es la fuente comercial recomendada para probar operación y resolución de atascos descrita para el usuario. Con los cinco `.md` simulados forma un paquete de **6 archivos de conocimiento y 403 fragmentos**. La implementación envía una llamada de embeddings por documento y hasta 50 fragmentos en cada llamada: estima **13 llamadas** para este paquete (8 para el PDF y 5 para los `.md`). Es una cantidad manejable para una carga de prueba, pero no una garantía de cuota: otras personas o consultas en el mismo proyecto, tokens consumidos, el límite diario y disponibilidad del modelo también cuentan. Las guías `.md` sirven para probar el flujo con los otros equipos; no son documentación del fabricante.

Si también necesitas probar contenido de servicio técnico, añade en una segunda etapa **`data/example_corpus/manuals/pdf_14048509_en-US-1.pdf`**, Repair Manual para una familia que incluye MFP 5602. Es adecuado solo para probar recuperación de procedimientos de servicio y seguridad, y sus indicaciones deben limitarse a personal autorizado. Es un archivo grande: 54.5 MB y aproximadamente 1,866 fragmentos. No lo incluyas en la primera carga gratuita; indexarlo elevaría el total a cerca de 2,269 fragmentos y 51 llamadas de embeddings.

No uses como manual comercial de mantenimiento **`IDEAL_5560-5560_LT_engl.pdf`** (folleto de producto), **`KODAK-NEXPRESS-DIG-v20.0.pdf`** ni **`KODAK-NEXPRESS-DIR-v22.pdf`** (documentación de interfaz, útil solo para pruebas de integración/comandos), ni **`c03985204.pdf`** (manual de servicio ZBook de generación anterior, modelo exacto sin confirmar). Mantén también excluidos los PDFs auxiliares agrupados en la última fila de `manual_sources.csv`.

Las **100 órdenes sintéticas** son un conjunto aparte: generan 100 fragmentos. Como la aplicación procesa cada archivo por separado, requieren aproximadamente **100 llamadas de embeddings**, no dos llamadas por lote. Cárgalas en lotes de 25 archivos como indica esta guía, dejando tiempo entre tandas y comprobando los límites activos. Con el paquete de seis fuentes más las 100 órdenes se estiman 503 fragmentos y **113 llamadas** de embeddings en total. Deja para una fase posterior el manual de servicio HP de 1,866 fragmentos; no cargues PDFs auxiliares excluidos ni manuales sin correspondencia confirmada.

Si aparece `429 RESOURCE_EXHAUSTED`, detén nuevas cargas y respeta el `retryDelay` indicado; revisa cuota diaria y límites activos antes de reanudar. Un `503 UNAVAILABLE` significa que el modelo está temporalmente saturado, no que se excedió la cuota; vuelve a intentar más tarde. Las cuotas cambian y Google no garantiza capacidad fija.

## 4. Iniciar FastAPI y Streamlit

Mantén dos terminales abiertas, ambas ubicadas en la raíz del proyecto y con `.venv` activo.

En la primera, inicia FastAPI:

```bash
uvicorn app.main:app --reload --port 8000
```

En la segunda, inicia Streamlit:

```bash
streamlit run ui/streamlit_app.py --server.port 8501
```

Abre `http://localhost:8501`. La parte superior debe mostrar que la API está conectada y que hay cero documentos y fragmentos después del reinicio. Si necesitas consultar el estado, usa `http://localhost:8000/health`; `http://localhost:8000/docs` es la referencia técnica de FastAPI, no otra UI del proyecto.

## 5. Cargar los documentos de ejemplo

En Streamlit abre la pestaña **Cargar documentos**.

1. Selecciona **Manual técnico**.
2. Para el paquete gratuito inicial, selecciona los cinco `.md` de `data/example_corpus/manuals/` y `data/example_corpus/manuals/pdf_11954803_en-US-1.pdf`. Ese es el manual comercial recomendado para pruebas de usuario. Añade `pdf_14048509_en-US-1.pdf` solo en una segunda etapa si necesitas probar servicio técnico y tienes el contexto de personal autorizado; su tamaño y 1,866 fragmentos aumentan considerablemente la carga. No selecciones el folleto IDEAL, las referencias de interfaz Kodak, el manual ZBook de generación no confirmada ni los PDFs auxiliares.
3. Deja **Identificador del equipo** vacío para esta carga conjunta: las guías cubren distintos equipos y no deben recibir todas el mismo identificador.
4. Pulsa **Indexar documentos** y espera la confirmación de documentos y fragmentos.
5. Selecciona **Orden de trabajo PDF**.
6. Selecciona los cien PDFs de `data/example_corpus/work_orders/` para consultas generales, dejándolos sin ID; si la ingesta tarda o se interrumpe, carga los archivos por lotes de 25.
7. Pulsa **Indexar documentos** y espera la confirmación.

Si después quieres probar **Plan de mantenimiento** con filtro por equipo, carga por separado los documentos de cada activo y asigna el ID correspondiente. Hay 25 órdenes por equipo: `PRN-HP-01`, `CUT-IDEAL-01`, `PC-HP-01` y `PRN-KODAK-01`. No asignes un solo ID a documentos de varios equipos. La búsqueda filtrada depende del ID proporcionado al cargarlos. El límite es 75 MB por archivo; la interfaz presenta bytes, páginas, idioma estimado y fragmentos tras indexar.

Las guías técnicas del corpus están marcadas como simuladas y no son manuales oficiales ni instrucciones para intervenir equipos reales.

## 6. Confirmar conteos y parámetros

Consulta `http://localhost:8000/health`. Con todo el corpus de ejemplo ingerido y la configuración predeterminada, debe mostrar:

| Métrica | Esperado |
|---|---:|
| `index.manual_documents` | 6 con el paquete inicial (cinco `.md` y una guía HP); 5 si omites el PDF |
| `index.work_order_documents` | 100 |
| `index.total_documents` | 106 con seis fuentes iniciales y 100 órdenes (105 si omites la guía HP) |
| `index.total_chunks` | Variable; revisa el valor real en `/health` |
| `chunking.size_words` / `chunking.overlap_words` | 300 / 60 |
| `abstention.minimum_relevance_score` | 0.35 |

Los conteos de chunks cambian si editas los archivos, los límites por página o la configuración de chunking. La cantidad de documentos cuenta nombres de archivo distintos dentro de cada colección. La carga posterior de un archivo con el mismo nombre y tipo de fuente reemplaza sus fragmentos anteriores. La búsqueda bilingüe no duplica los chunks indexados.

## 7. Probar respuesta con citas y abstención

En **Consultar**, deja la búsqueda en **Ambas fuentes** y pregunta:

> ¿Qué información conviene registrar cuando una impresora presenta variación de calidad?

Verifica que la respuesta esté en español, incluya referencias `[n]` y que cada referencia se corresponda con un fragmento visible en **Fuentes recuperadas**, incluyendo nombre de archivo y score.

Luego prueba una pregunta que no esté en el corpus:

> ¿Cuál es la capital de Islandia?

La UI debe mostrar que el sistema se abstuvo y explicar que falta evidencia suficiente. La API debe responder normalmente; una pregunta fuera de dominio no debería producir un error 500.

Google AI genera los embeddings de los documentos y de la pregunta; se usa el mismo modelo de embedding en ambos casos. Chroma persiste los fragmentos, vectores y metadatos, y devuelve los vecinos `top-k`. Gemini recibe la pregunta y los fragmentos recuperados para redactar la respuesta; no se arma la respuesta concatenando fragmentos sin generación.

## 8. Confirmar persistencia al reiniciar FastAPI

Deja los documentos ingeridos y detén solamente FastAPI con `Ctrl+C`. No muevas ni respaldes Chroma en esta prueba. Vuelve a ejecutar:

```bash
uvicorn app.main:app --reload --port 8000
```

Consulta `/health`: debe conservar los conteos previos (105 documentos si cargaste solo las cinco guías `.md` y las 100 órdenes; más los manuales comerciales que hayas seleccionado). Repite una pregunta en español respaldada por el manual inglés y comprueba que las citas sigan apuntando al texto original. Streamlit puede permanecer abierto; si muestra una desconexión momentánea, espera a que FastAPI esté disponible y vuelve a enviar la consulta.

## 9. Problemas frecuentes y reporte

- **API desconectada:** confirma que Uvicorn siga ejecutándose en el puerto 8000. Reinicia FastAPI y recarga Streamlit.
- **Clave ausente:** verifica localmente `GOOGLE_API_KEY` en `.env` y consulta `google_api_key_configured` en `/health`; nunca pegues la clave en logs o capturas.
- **Formato rechazado:** carga solo PDF, Markdown o TXT. Convierte el Excel a PDFs con el generador; no lo subas.
- **PDF sin texto:** requiere OCR antes de la ingesta; confirma que el texto sea seleccionable.
- **Error de Google AI o cuota:** revisa acceso y disponibilidad de la clave/modelos en la API de Google AI Studio; conserva los archivos y reintenta cuando el servicio esté disponible.
- **No hay citas o hay abstención:** confirma los conteos en `/health`, quita filtros de equipo que no aplican y formula una pregunta cuya respuesta esté en los documentos cargados.

Para el reporte corto de una página, copia desde `/health` los conteos `index`, los modelos `models`, el límite `ingestion.max_upload_size_mb`, la partición `chunking` y el umbral `abstention.minimum_relevance_score`. Anota fecha y fuentes cargadas; explica que las preguntas en español también buscan con una traducción inglesa y que Chroma conserva solo fragmentos originales. Indica la regla de abstención: no generar respuesta si ningún fragmento recuperado alcanza el score mínimo configurado.
