import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


from app.chunk import chunk_pages
from app.documents import detect_language, extract_pages
from app.embed import GoogleAIEmbeddings
from app.generate import answer_with_evidence
from app.rag import RAGService
from app.store import VectorStore


class DocumentTests(unittest.TestCase):
    def test_text_is_split_with_overlap(self):
        pages = extract_pages("manual.txt", "uno dos tres cuatro cinco seis".encode())
        chunks = chunk_pages(pages, size=4, overlap=1)
        self.assertEqual([item[0] for item in chunks], ["uno dos tres cuatro", "cuatro cinco seis"])

    def test_source_language_is_recorded_for_english_and_spanish(self):
        self.assertEqual(detect_language("The printer maintenance guide describes troubleshooting."), "en")
        self.assertEqual(detect_language("¿Cómo se limpia la impresora?"), "es")
        page = extract_pages("manual.txt", b"The printer maintenance guide describes troubleshooting.")[0]
        self.assertEqual(page.language, "en")

    def test_unsupported_file_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Formato no admitido"):
            extract_pages("orders.xlsx", b"not a document")

    def test_chunking_rejects_overlap_larger_than_chunk(self):
        pages = extract_pages("manual.txt", b"uno dos tres")
        with self.assertRaisesRegex(ValueError, "mayor que el solapamiento"):
            chunk_pages(pages, size=2, overlap=2)

    def test_reingesting_same_file_replaces_old_chunks(self):
        with tempfile.TemporaryDirectory() as directory:
            config = SimpleNamespace(chroma_directory=Path(directory))
            with patch("app.store.get_settings", return_value=config):
                store = VectorStore()
                store.add_chunks("work_order", "OT-1.pdf", [("texto viejo", None, 0)], [[1.0, 0.0]], "EQ-1")
                store.add_chunks("work_order", "OT-1.pdf", [("texto actualizado", None, 0)], [[0.0, 1.0]], "EQ-1")
                self.assertEqual(store.work_orders.count(), 1)
                saved = store.work_orders.get(include=["documents"])
                self.assertEqual(saved["documents"], ["texto actualizado"])
                matches = store.search([0.0, 1.0], 1, "work_order", "EQ-1")
                self.assertEqual(matches[0]["source"], "OT-1.pdf")
                self.assertEqual(matches[0]["equipment_id"], "EQ-1")
                self.assertEqual(store.status(), {
                    "manual_documents": 0, "manual_chunks": 0,
                    "work_order_documents": 1, "work_order_chunks": 1,
                    "total_documents": 1, "total_chunks": 1,
                })


class GroundingTests(unittest.TestCase):
    def test_api_documents_required_endpoints(self):
        from app.main import app

        paths = app.openapi()["paths"]
        self.assertTrue({"/health", "/ingest", "/query", "/maintenance-plan"}.issubset(paths))

    def test_citation_numbers_match_visible_retrieval_order(self):
        class Models:
            prompt = ""

            def generate_content(self, **kwargs):
                self.prompt = kwargs["contents"]
                return SimpleNamespace(text="Respuesta con cita [2].")

        service = RAGService.__new__(RAGService)
        service.settings = SimpleNamespace(min_relevance_score=0.35, google_generation_model="test-model")
        service.client = SimpleNamespace(models=Models())
        citations = [
            {"source": "irrelevante.txt", "text": "ruido", "score": 0.2},
            {"source": "manual.pdf", "text": "El sensor requiere limpieza periódica.", "score": 0.8},
        ]
        answer, abstained = service.answer("¿Qué requiere el sensor?", citations)
        self.assertFalse(abstained)
        self.assertIn("[2] Fuente: manual.pdf", service.client.models.prompt)
        self.assertIn("[2]", answer)

    def test_abstention_does_not_call_generation_below_threshold(self):
        class Models:
            called = False

            def generate_content(self, **_kwargs):
                self.called = True
                return SimpleNamespace(text="No debería generarse")

        models = Models()
        answer, abstained = answer_with_evidence(
            SimpleNamespace(models=models), "test-model", "¿Cuál es la respuesta?",
            [{"source": "irrelevante.txt", "text": "sin relación", "score": 0.1}], 0.35,
        )
        self.assertTrue(abstained)
        self.assertIn("evidencia suficiente", answer)
        self.assertFalse(models.called)

    def test_embedding_client_uses_configured_model_and_task_type(self):
        class Models:
            def embed_content(self, **kwargs):
                self.kwargs = kwargs
                return SimpleNamespace(embeddings=[SimpleNamespace(values=[0.1, 0.2])])

        models = Models()
        embedding = GoogleAIEmbeddings(SimpleNamespace(models=models), "embedding-model")
        vectors = embedding.embed(["texto"], "RETRIEVAL_QUERY")
        self.assertEqual(vectors, [[0.1, 0.2]])
        self.assertEqual(models.kwargs["model"], "embedding-model")
        self.assertEqual(models.kwargs["config"].task_type, "RETRIEVAL_QUERY")

    def test_spanish_query_uses_translation_and_keeps_original_source_citation(self):
        class Models:
            def generate_content(self, **_kwargs):
                return SimpleNamespace(text="paper jam in the feed tray")

        class Store:
            def __init__(self):
                self.vectors = []

            def search(self, vector, _top_k, _source_type, _equipment_id):
                self.vectors.append(vector)
                return [{"id": "manual:page-1", "source": "repair.pdf", "page": 12,
                         "text": "Original English evidence", "score": 0.81,
                         "source_type": "manual"}]

        service = RAGService.__new__(RAGService)
        service.settings = SimpleNamespace(google_generation_model="test-model")
        service.client = SimpleNamespace(models=Models())
        service.store = Store()
        embedded = []

        def embed(texts, task_type):
            embedded.extend(texts)
            self.assertEqual(task_type, "RETRIEVAL_QUERY")
            return [[float(index), 1.0] for index, _text in enumerate(texts)]

        service.embed = embed
        results = service.retrieve("¿Dónde se atasca el papel?", 2, "manual")
        self.assertEqual(embedded, ["¿Dónde se atasca el papel?", "paper jam in the feed tray"])
        self.assertEqual(len(service.store.vectors), 2)
        self.assertEqual(len(results), 1)
        self.assertEqual((results[0]["source"], results[0]["page"], results[0]["text"]),
                         ("repair.pdf", 12, "Original English evidence"))

    def test_health_exposes_report_configuration_and_index_counts(self):
        from app.main import health

        settings = SimpleNamespace(
            google_api_key="configured", google_embedding_model="embed-model",
            google_generation_model="gen-model", chunk_size_words=300,
            chunk_overlap_words=60, min_relevance_score=0.35,
            max_upload_size_mb=75,
        )
        counts = {"manual_documents": 5, "manual_chunks": 9,
                  "work_order_documents": 20, "work_order_chunks": 22,
                  "total_documents": 25, "total_chunks": 31}
        with patch("app.main.get_settings", return_value=settings), \
                patch("app.main.get_store") as get_store:
            get_store.return_value.status.return_value = counts
            body = health()
        self.assertEqual(body["models"]["embedding"], "embed-model")
        self.assertEqual(body["chunking"]["overlap_words"], 60)
        self.assertEqual(body["abstention"]["minimum_relevance_score"], 0.35)
        self.assertEqual(body["index"]["total_documents"], 25)
        self.assertEqual(body["ingestion"]["max_upload_size_mb"], 75)


if __name__ == "__main__":
    unittest.main()
