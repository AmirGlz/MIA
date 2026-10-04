# Corpus de ejemplo

Este corpus demuestra la ingesta desde Streamlit en el dominio de mantenimiento de un taller de impresión.

- `manuals/`: cinco guías originales de simulación y PDFs comerciales añadidos localmente. Consulta `../../corpus_builder/input/manual_sources.csv`: el manual HP 5602 y la guía ZBook tienen alcance de servicio con sus advertencias; el archivo IDEAL es solo un folleto; los PDF Kodak describen interfaces; otros accesorios y documentos generales están excluidos del índice de mantenimiento. Las guías sintéticas no son documentación oficial y no deben usarse para intervenir equipos reales.
- `work_orders/`: 100 PDFs sintéticos reproducibles, 25 por cada uno de cuatro equipos, creados desde `corpus_builder/input/work_orders_master.xlsx`. No son historiales de intervenciones reales.

Para regenerar las órdenes, ejecuta los comandos descritos en [`corpus_builder/README.md`](../../corpus_builder/README.md). En Streamlit carga solo las fuentes elegidas del catálogo y los PDFs de órdenes. No cargues todos los PDFs de `manuals/` en bloque. Ningún archivo se ingiere automáticamente; el Excel nunca se carga.
