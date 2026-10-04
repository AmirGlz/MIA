# Guía para preparar manuales técnicos

## 1. Seleccionar equipos y documentación

1. Define el equipo de la imprenta y asigna un `equipment_id` estable, por ejemplo `PRN-HP-01` o `CUT-01`.
2. Localiza la guía de usuario, mantenimiento o diagnóstico en el sitio oficial del fabricante. Ejemplos de portales para comenzar: [Kodak Workflow Documentation](https://workflowhelp.kodak.com/), [HP Support](https://support.hp.com/) e [IDEAL](https://ideal.de/en/).
3. Verifica que el documento corresponda exactamente al fabricante y modelo del catálogo. No atribuyas a un equipo instrucciones de otro modelo.
4. Registra en `corpus_builder/input/manual_sources.csv`: equipo, fabricante, modelo, título, URL, tipo de guía, fecha de consulta, idioma, permiso/condición de redistribución, ruta local y alcance permitido para indexación.
5. Comprueba que el archivo tenga texto seleccionable. Si es un PDF escaneado, aplica OCR antes de subirlo.

## 2. Guardar y preparar las fuentes

- Conserva el nombre original si es descriptivo; de lo contrario usa `fabricante_modelo_tipo_fecha.pdf`.
- Guarda los manuales que se puedan redistribuir en `data/example_corpus/manuals/`. Para fuentes restringidas, no copies el PDF al repositorio: deja la URL y pasos de descarga en el catálogo.
- Conserva portada, título y número de página al procesar documentos. El sistema registra nombre de archivo y página como metadatos de cada fragmento.
- No reescribas ni presentes texto sintético como una indicación oficial. Si se producen resúmenes didácticos, identifícalos como resúmenes y conserva la referencia a la fuente.

`input/manual_sources.csv` indica ruta local y alcance previsto de cada fuente. No cargues por defecto PDFs de accesorios, BIOS, avisos regulatorios, equipos distintos o documentos sin alcance de mantenimiento. En el corpus actual, el PDF IDEAL local es un folleto de producto de dos páginas y no sustituye el manual oficial de operación; los PDFs Kodak locales son especificaciones de interfaz y no instrucciones de reparación física. El manual de servicio ZBook local debe cotejarse con la generación exacta.

Antes de cargar fuentes grandes, ejecuta `.venv/bin/python corpus_builder/scripts/inspect_manuals.py`. El reporte estima bytes, páginas, palabras, idiomas y cantidad de fragmentos con la configuración activa, sin generar embeddings ni enviar texto a Google. Las fuentes marcadas como excluidas solo se reportan por tamaño y no se extraen.

### Selección inicial para el nivel gratuito de Gemini

Carga solo estas fuentes del catálogo para empezar:

| Fuente | Tamaño | Fragmentos | Uso |
|---|---:|---:|---|
| `pdf_11954803_en-US-1.pdf` (HP MFP 5602, guía de usuario) | 9.6 MB | 389 | Fuente oficial para operación y atascos |
| `01_impresora_produccion.md` | 3.9 KB | 3 | Simulación para preguntas de impresora |
| `02_cortadora_papel.md` | 3.9 KB | 3 | Simulación para cortadora IDEAL |
| `03_prensa_digital.md` | 3.9 KB | 3 | Simulación para Kodak NEXPRESS |
| `04_estacion_preprensa.md` | 3.9 KB | 3 | Simulación para ZBook |
| `05_sistema_aire_taller.md` | 3.7 KB | 2 | Simulación del sistema de aire |

El paquete suma **403 fragmentos**. La aplicación hace llamadas por documento y envía hasta 50 fragmentos por llamada: estima 13 llamadas para este paquete (8 para el PDF HP y una por cada `.md`). No cargues de inicio los **2,779 fragmentos** de todas las fuentes incluidas en el catálogo. Las guías `.md` son simulaciones del proyecto, no manuales del fabricante. El manual de servicio HP `pdf_14048509_en-US-1.pdf` queda para una segunda fase: por sí solo son 54.5 MB, 1,866 fragmentos y 38 llamadas. No cargues los PDFs auxiliares marcados como excluidos ni los dos documentos Kodak de interfaz para consultas de reparación física.

La cuota del nivel gratuito depende del proyecto, modelo y ventana activa, y puede cambiar; esta selección reduce el trabajo inicial, pero no garantiza una cuota fija. Indexa en dos tandas: primero la guía HP y luego los cinco `.md`. Si Google devuelve `429`, espera el intervalo indicado y revisa el uso antes de reintentar.

## 3. Cargar a la aplicación

1. Ejecuta FastAPI y Streamlit siguiendo el README.
2. En Streamlit, abre **Cargar documentos**, selecciona **Manual técnico** y los documentos.
3. Escribe el identificador del equipo cuando corresponda; esto permite filtrar consultas por activo.
4. Confirma que la UI muestre los documentos y fragmentos indexados. Si el PDF no contiene texto, se notificará para que se aplique OCR.
5. Haz preguntas cuya respuesta esté en el manual y verifica que la cita muestre el archivo, la página y el texto recuperado.

Los fragmentos se crean con ventanas de hasta 300 palabras y solapamiento de 60 palabras. Se guarda el idioma detectado como metadato. Para preguntas detectadas en español, la recuperación también genera una traducción de la consulta al inglés y combina los resultados, deduplicando los mismos fragmentos. Los documentos no se traducen ni duplican en el índice; las citas conservan texto y página originales. Ambos vectores de consulta y documento usan el mismo modelo Google AI. La colección de manuales se llama `manual_chunks`.

La ingesta informa bytes, páginas extraídas, idiomas y fragmentos para revisar el tamaño antes de indexar. Se aceptan PDFs de hasta 75 MB; un archivo grande aún puede producir miles de fragmentos y consumir cuota de embeddings. Selecciona únicamente fuentes del catálogo pertinentes al equipo.

Si falla un archivo, revisa `logs/ingestion.log` en el directorio de la API. El registro conserva fecha, archivo, tipo de fuente y traza técnica; rota al llegar a 5 MB y mantiene hasta cinco copias. Puedes cambiar la ruta con `INGESTION_LOG_PATH`.

Ante un `429 RESOURCE_EXHAUSTED` temporal, la API espera el intervalo `retryDelay` indicado por Google y vuelve a intentar el lote de embeddings hasta dos veces. Si el error no incluye un intervalo de reintento (por ejemplo, una cuota diaria agotada), revisa el uso y el plan del proyecto de Google AI; la aplicación registra y muestra el fallo.

## 4. Catálogo de fuentes

El archivo `corpus_builder/input/manual_sources.csv` registra los documentos de referencia. Agrega una fila por documento y actualiza la fecha de consulta cuando cambie la fuente. El corpus de ejemplo también incluye guías sintéticas originales; están marcadas como simulación y no reemplazan los manuales oficiales ni describen procedimientos autorizados para equipos reales.
