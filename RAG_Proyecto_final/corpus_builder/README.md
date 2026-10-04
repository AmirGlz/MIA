# Constructor del corpus de ejemplo

Esta carpeta contiene únicamente las fuentes y herramientas para preparar documentos. No llama a FastAPI, ChromaDB ni Google AI.

- `input/work_orders_master.xlsx`: Excel fuente, una orden por fila; nunca se ingiere.
- `input/equipment_catalog.csv`: catálogo que valida equipo, modelo y fuente de referencia.
- `input/manual_sources.csv`: procedencia y naturaleza de los documentos técnicos.
- `scripts/validate_dataset.py`: valida el Excel contra el catálogo.
- `scripts/build_demo_work_orders.py`: recrea las 100 órdenes sintéticas aprobadas en el Excel maestro, 25 por equipo.
- `scripts/inspect_manuals.py`: informa tamaño, texto, páginas y fragmentos estimados antes de indexar; no llama a Google AI y omite el procesamiento de fuentes marcadas como excluidas.
- `scripts/validate_example_corpus.py`: confirma que el corpus contiene guías, PDFs, texto extraíble y el mínimo de documentos/palabras.
- `scripts/generate_work_orders.py`: produce un PDF sintético por orden en `../data/example_corpus/work_orders/`.
- `docs/`: instrucciones reproducibles para mantener fuentes y generar órdenes.
- `docs/guia_inicio_a_fin.md`: procedimiento completo para respaldar/reiniciar Chroma, cargar el corpus desde Streamlit, probar citas y abstención, y comprobar persistencia.

Desde la raíz del repositorio, ejecuta:

```bash
python corpus_builder/scripts/build_demo_work_orders.py
python corpus_builder/scripts/inspect_manuals.py
python corpus_builder/scripts/validate_dataset.py
python corpus_builder/scripts/generate_work_orders.py
python corpus_builder/scripts/validate_example_corpus.py
```

Luego carga en Streamlit los PDFs resultantes y las fuentes manuales aprobadas según `input/manual_sources.csv`; no selecciones todos los PDFs de `data/example_corpus/manuals/`. La app procesa exclusivamente los archivos seleccionados en la UI. Para probar planes por equipo, carga las 25 órdenes de cada equipo en un lote separado y asígnales el ID correcto.

Para ejecutar el ciclo completo desde el reinicio del índice hasta las pruebas, sigue [`docs/guia_inicio_a_fin.md`](docs/guia_inicio_a_fin.md).
