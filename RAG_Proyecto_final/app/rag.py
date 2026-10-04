from google import genai
from app.config import get_settings
from app.chunk import chunk_pages
from app.documents import detect_language, extract_pages
from app.embed import GoogleAIEmbeddings
from app.generate import answer_with_evidence
from app.store import get_store


class RAGService:
    def __init__(self) -> None:
        self.settings = get_settings()
        if not self.settings.google_api_key:
            raise RuntimeError("Falta GOOGLE_API_KEY en el archivo .env.")
        self.client = genai.Client(api_key=self.settings.google_api_key)
        self.embeddings = GoogleAIEmbeddings(self.client, self.settings.google_embedding_model)
        self.store = get_store()

    def embed(self, texts: list[str], task_type: str):
        return self.embeddings.embed(texts, task_type)

    def ingest(self, filename: str, content: bytes, source_type: str, equipment_id: str | None):
        pages = extract_pages(filename, content)
        chunks = chunk_pages(pages, self.settings.chunk_size_words,
                             self.settings.chunk_overlap_words)
        # The indexed source stays authoritative. Cross-language recall is added
        # at query time, avoiding a second translated copy of very large manuals.
        vectors = self.embed([chunk[0] for chunk in chunks], "RETRIEVAL_DOCUMENT")
        count = self.store.add_chunks(source_type, filename, chunks, vectors, equipment_id)
        languages = sorted({page.language for page in pages if page.language})
        return {"filename": filename, "source_type": source_type, "bytes": len(content),
                "pages_extracted": len(pages), "source_languages": languages,
                "chunks_indexed": count}

    def retrieve(self, query: str, top_k: int, source_type: str | None = None,
                 equipment_id: str | None = None):
        query_forms = [query]
        if detect_language(query) == "es":
            translated = self._translate_query(query, "English")
            if translated and translated.casefold() != query.casefold():
                query_forms.append(translated)
        vectors = self.embed(query_forms, "RETRIEVAL_QUERY")
        candidates = []
        for vector in vectors:
            candidates.extend(self.store.search(vector, max(top_k * 3, top_k),
                                                source_type, equipment_id))
        # Collapse the same indexed chunk retrieved by both language queries.
        best = {}
        for item in candidates:
            key = item["id"]
            if key not in best or item["score"] > best[key]["score"]:
                best[key] = item
        return sorted(best.values(), key=lambda item: item["score"], reverse=True)[:top_k]

    def _translate_query(self, query: str, target_language: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.settings.google_generation_model,
                contents=(f"Translate the following maintenance search query into {target_language}. "
                          "Preserve equipment model names, part names, and error codes. "
                          "Return only the translation; do not answer the query.\n\n" + query),
            )
            return (response.text or "").strip()
        except Exception:
            # Original-language retrieval remains available during provider outages.
            return ""

    def answer(self, question: str, citations: list[dict]):
        return answer_with_evidence(
            self.client, self.settings.google_generation_model, question,
            citations, self.settings.min_relevance_score,
        )

    def query(self, question: str, top_k: int, source_type: str | None = None,
              equipment_id: str | None = None):
        citations = self.retrieve(question, top_k, source_type, equipment_id)
        answer, abstained = self.answer(question, citations)
        return {"answer": answer, "citations": citations, "abstained": abstained}

    def maintenance_plan(self, equipment_id: str, top_k: int):
        actions = []
        order_query = f"Historial de fallas, reparaciones y mantenimiento del equipo {equipment_id}"
        orders = self.retrieve(order_query, top_k, "work_order", equipment_id)
        actions.append({"tool": "search_work_orders", "observation": f"Se recuperaron {len(orders)} órdenes."})
        manual_query = f"Procedimientos, mantenimiento preventivo y solución de problemas para {equipment_id}"
        manuals = self.retrieve(manual_query, top_k, "manual", equipment_id)
        actions.append({"tool": "search_manuals", "observation": f"Se recuperaron {len(manuals)} fragmentos de manual."})
        citations = sorted(orders + manuals, key=lambda item: item["score"], reverse=True)[:top_k * 2]
        if not citations:
            return {"answer": "No tengo evidencia suficiente para proponer un plan.",
                    "citations": [], "abstained": True, "actions": actions}
        answer, abstained = self.answer(
            f"Propón un plan de mantenimiento para {equipment_id}. Separa acciones sugeridas, "
            "motivo sustentado en el manual o historial y prioridad. Distingue patrones inferidos "
            "de instrucciones textuales.", citations)
        return {"answer": answer, "citations": citations, "abstained": abstained, "actions": actions}
