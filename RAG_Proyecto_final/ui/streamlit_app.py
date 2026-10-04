import os
import json

import requests
import streamlit as st

API_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def api_error_message(response, prefix: str) -> str:
    try:
        body = response.json()
        detail = body.get("detail", body)
        return f"{prefix}: {json.dumps(detail, ensure_ascii=False)}"
    except (ValueError, AttributeError):
        return f"{prefix}: {response.text or response.reason}"


st.set_page_config(page_title="Asistente de mantenimiento", page_icon="🛠️", layout="wide")
st.title("Asistente de mantenimiento")
st.caption("Consulta manuales y órdenes de trabajo con respuestas respaldadas por fuentes.")

try:
    health = requests.get(f"{API_URL}/health", timeout=5)
    health.raise_for_status()
    state = health.json()
    st.success(
        f"API conectada · {state['index']['total_documents']} documentos · "
        f"{state['index']['total_chunks']} fragmentos "
        f"({state['index']['manual_documents']} manuales, "
        f"{state['index']['work_order_documents']} órdenes)"
    )
    if not state.get("google_api_key_configured"):
        st.warning("Falta configurar GOOGLE_API_KEY en el archivo .env de la API.")
except requests.RequestException:
    st.error(f"No se puede conectar a la API en {API_URL}. Inicia FastAPI y vuelve a cargar la página.")
    state = None

ingest_tab, query_tab, plan_tab = st.tabs(["Cargar documentos", "Consultar", "Plan de mantenimiento"])
with ingest_tab:
    st.subheader("Ingesta de documentos")
    st.write("Carga PDF, Markdown o TXT. Los Excel no se ingieren: genera primero los PDF de órdenes.")
    with st.form("ingest_form", clear_on_submit=True):
        source_type = st.selectbox("Tipo de fuente", ["manual", "work_order"],
                                  format_func=lambda value: "Manual técnico" if value == "manual" else "Orden de trabajo PDF")
        equipment_id = st.text_input("Identificador del equipo (opcional)", placeholder="PRN-KODAK-01")
        max_upload_mb = state.get("ingestion", {}).get("max_upload_size_mb", 75) if state else 75
        files = st.file_uploader(f"Archivos (límite por archivo: {max_upload_mb} MB)",
                                 type=["pdf", "md", "txt"], accept_multiple_files=True,
                                 max_upload_size=max_upload_mb)
        submitted = st.form_submit_button("Indexar documentos", type="primary")
    if submitted:
        if not files:
            st.warning("Selecciona al menos un documento.")
        elif not state:
            st.error("La API no está disponible.")
        else:
            payload = [("files", (item.name, item.getvalue(), item.type or "application/octet-stream")) for item in files]
            try:
                response = requests.post(f"{API_URL}/ingest", data={"source_type": source_type,
                                      "equipment_id": equipment_id}, files=payload, timeout=180)
                if response.ok:
                    result = response.json()
                    st.success(f"Documentos indexados: {result['documents_indexed']} · "
                               f"fragmentos nuevos/actualizados: {result['chunks_indexed']}")
                    for item in result.get("files", []):
                        languages = ", ".join(item.get("source_languages", [])) or "desconocido"
                        st.caption(f"{item['filename']}: {item.get('bytes', 0):,} bytes · "
                                   f"{item.get('pages_extracted', 0)} páginas · "
                                   f"{item['chunks_indexed']} fragmentos · idioma {languages}")
                    for error in result.get("errors", []):
                        st.warning(f"{error['filename']}: {error['error']}")
                else:
                    st.error(response.text)
            except requests.RequestException as exc:
                st.error(f"Falló la ingesta: {exc}")

with query_tab:
    st.subheader("Pregunta sobre el corpus")
    with st.form("query_form"):
        question = st.text_area("Pregunta", placeholder="¿Qué fallas recurrentes presenta PRN-KODAK-01?")
        source_filter = st.selectbox("Buscar en", ["Ambas fuentes", "Manuales", "Órdenes de trabajo"])
        equipment_filter = st.text_input("Filtrar por equipo (opcional)", key="query_equipment")
        top_k = st.slider("Fragmentos a recuperar por fuente", 1, 10, 4)
        ask = st.form_submit_button("Consultar", type="primary")
    if ask:
        if not question.strip():
            st.warning("Escribe una pregunta.")
        elif not state:
            st.error("La API no está disponible.")
        else:
            source_type = {"Ambas fuentes": None, "Manuales": "manual", "Órdenes de trabajo": "work_order"}[source_filter]
            try:
                response = requests.post(f"{API_URL}/query", json={"question": question,
                    "top_k": top_k, "source_type": source_type,
                    "equipment_id": equipment_filter or None}, timeout=120)
                response.raise_for_status()
                result = response.json()
                st.markdown("### Respuesta")
                st.write(result["answer"])
                if result["abstained"]:
                    st.info("El sistema se abstuvo porque no encontró evidencia suficiente.")
                st.markdown("### Fuentes recuperadas")
                if not result["citations"]:
                    st.info("El índice está vacío o no hay fragmentos para ese equipo.")
                for index, citation in enumerate(result["citations"], start=1):
                    label = f"[{index}] {citation['source']} · relevancia {citation['score']:.3f}"
                    if citation.get("page"):
                        label += f" · página {citation['page']}"
                    with st.expander(label):
                        language = citation.get("language") or "desconocido"
                        st.caption(f"Tipo: {citation['source_type']} · "
                                   f"Equipo: {citation.get('equipment_id') or 'sin asignar'} · "
                                   f"Idioma fuente: {language}")
                        st.write(citation["text"])
            except requests.HTTPError as exc:
                st.error(api_error_message(exc.response, "No se pudo consultar"))
            except requests.RequestException as exc:
                st.error(f"No se pudo consultar: {exc}")

with plan_tab:
    st.subheader("Proponer mantenimiento")
    with st.form("plan_form"):
        plan_equipment = st.text_input("Identificador del equipo", placeholder="PRN-KODAK-01")
        plan_top_k = st.slider("Fragmentos por fuente", 1, 10, 4, key="plan_top_k")
        plan = st.form_submit_button("Generar plan", type="primary")
    if plan:
        if not plan_equipment.strip():
            st.warning("Indica el identificador del equipo.")
        elif not state:
            st.error("La API no está disponible.")
        else:
            try:
                response = requests.post(f"{API_URL}/maintenance-plan", json={
                    "equipment_id": plan_equipment, "top_k": plan_top_k}, timeout=120)
                response.raise_for_status()
                result = response.json()
                st.markdown("### Plan propuesto")
                st.write(result["answer"])
                if result["abstained"]:
                    st.info("Evidencia insuficiente para proponer un plan.")
                with st.expander("Herramientas utilizadas"):
                    for action in result.get("actions", []):
                        st.write(f"{action['tool']}: {action['observation']}")
                st.markdown("### Fuentes")
                for index, citation in enumerate(result["citations"], start=1):
                    with st.expander(f"[{index}] {citation['source']} · relevancia {citation['score']:.3f}"):
                        st.write(citation["text"])
            except requests.HTTPError as exc:
                st.error(api_error_message(exc.response, "No se pudo generar el plan"))
            except requests.RequestException as exc:
                st.error(f"No se pudo generar el plan: {exc}")
