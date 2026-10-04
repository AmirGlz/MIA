# Guía para generar órdenes sintéticas en PDF

## Propósito y límites

Las órdenes son datos ficticios de demostración. El Excel maestro es su fuente estructurada para generación; la aplicación indexa exclusivamente los PDFs generados y cargados desde Streamlit. No cargues el Excel como documento RAG.

## 1. Preparar el catálogo

El constructor actual está definido para cuatro IDs (`PRN-HP-01`, `CUT-IDEAL-01`, `PC-HP-01` y `PRN-KODAK-01`). Si agregas otro equipo, actualiza `equipment_catalog.csv` y también añade escenarios específicos y respaldados en `scripts/build_demo_work_orders.py`; cambiar solo el CSV no lo incorpora a las órdenes. Cada equipo requiere un ID, tipo, fabricante, modelo, descripción y URL de fuente verificada.

Define escenarios de falla basados en el equipo y las fuentes: síntomas, componentes, causas posibles y acciones preventivas o correctivas. Marca hipótesis sintéticas como ficticias; no inventes códigos de error atribuyéndolos a un fabricante.

## 2. Completar el Excel maestro

El generador espera `corpus_builder/input/work_orders_master.xlsx`, hoja `work_orders`, con estos encabezados:

`work_order_id`, `equipment_id`, `manufacturer`, `model`, `equipment_type`, `opened_at`, `closed_at`, `maintenance_type`, `reported_symptom`, `error_code`, `diagnosis`, `root_cause`, `actions_performed`, `parts_used`, `technician`, `downtime_hours`, `status`, `recommendations`, `notes`.

Usa una fila por orden, IDs únicos como `OT-0001`, equipo existente en el catálogo, fechas ISO `YYYY-MM-DD`, y fechas de cierre posteriores a las de apertura. `maintenance_type` admite `corrective`, `preventive` o `inspection`; `status` admite `closed` o `pending`. `error_code` y `parts_used` pueden quedar vacíos. Los nombres de técnicos deben ser ficticios.

El conjunto de demostración se recrea con `python corpus_builder/scripts/build_demo_work_orders.py`: crea 100 órdenes, 25 por equipo aprobado, con IDs únicos, fechas repartidas y casos correctivos, preventivos y de inspección. Las fuentes locales para IDEAL son un folleto, y las de Kodak describen interfaces de software; los escenarios se limitan a lo que esas fuentes acreditan. No presentes el folleto IDEAL como manual de servicio, ni la especificación Kodak como guía de reparación física. La guía de servicio ZBook corresponde a una generación anterior: confirma el submodelo. Las órdenes son ficticias, no describen fallas reales ni certifican procedimientos del fabricante.

## 3. Validar y generar PDFs

Activa el entorno virtual e instala los requisitos. Ejecuta:

```bash
python corpus_builder/scripts/build_demo_work_orders.py
python corpus_builder/scripts/validate_dataset.py
python corpus_builder/scripts/generate_work_orders.py
```

La validación revisa campos críticos, duplicados, fechas, catálogos, equipo y modelo. El generador crea un archivo `OT-XXXX.pdf` por fila en `data/example_corpus/work_orders/`, con secciones legibles y una marca visible de **orden sintética**. Corrige todos los errores reportados antes de indexar. Los PDFs de demostración pueden guardarse en Git; el Excel queda como entrada reproducible del constructor.

## 4. Ingestar los PDFs

En la única UI de usuario (Streamlit), selecciona **Orden de trabajo PDF**, carga los archivos de `data/example_corpus/work_orders/` y proporciona el identificador del equipo. La aplicación indexa cada PDF como historial; no lee el Excel ni consulta una base relacional.

Los fragmentos de órdenes se guardan en `work_order_chunks` con archivo, ID de orden y equipo. Un PDF por orden conserva trazabilidad y permite recuperar casos parecidos.
