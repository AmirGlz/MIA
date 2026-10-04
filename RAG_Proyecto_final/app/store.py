import hashlib
import re
from datetime import datetime, timezone

import chromadb

from app.config import get_settings


class VectorStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = chromadb.PersistentClient(path=str(settings.chroma_directory))
        self.manuals = self.client.get_or_create_collection("manual_chunks", metadata={"hnsw:space": "cosine"})
        self.work_orders = self.client.get_or_create_collection("work_order_chunks", metadata={"hnsw:space": "cosine"})

    def add_chunks(self, source_type: str, filename: str, chunks, embeddings, equipment_id: str | None):
        collection = self.manuals if source_type == "manual" else self.work_orders
        source = filename.replace("\\", "/").split("/")[-1]
        safe_source = re.sub(r"[^a-zA-Z0-9._-]+", "_", source)
        # Reingestar un archivo reemplaza su contenido anterior sin tocar otros documentos.
        collection.delete(where={"source": source})
        ids, documents, metadatas = [], [], []
        for index, chunk in enumerate(chunks):
            text, page, _, *extra = chunk
            language = extra[0] if extra else None
            digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
            ids.append(f"{source_type}:{safe_source}:{index}:{digest}")
            documents.append(text)
            metadata = {"source": source, "source_type": source_type, "chunk_index": index,
                        "indexed_at": datetime.now(timezone.utc).isoformat()}
            if page is not None:
                metadata["page"] = page
            if language:
                metadata["language"] = language
            if equipment_id:
                metadata["equipment_id"] = equipment_id.strip()
            if source_type == "work_order":
                order_id = source.rsplit(".", 1)[0]
                metadata["work_order_id"] = order_id
            metadatas.append(metadata)
        if ids:
            collection.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
        return len(ids)

    def search(self, query_embedding, top_k: int, source_type: str | None = None,
               equipment_id: str | None = None):
        targets = [("manual", self.manuals), ("work_order", self.work_orders)]
        if source_type:
            targets = [item for item in targets if item[0] == source_type]
        results = []
        for kind, collection in targets:
            if collection.count() == 0:
                continue
            where = {"equipment_id": equipment_id} if equipment_id else None
            response = collection.query(query_embeddings=[query_embedding], n_results=min(top_k, collection.count()),
                                        where=where, include=["documents", "metadatas", "distances"])
            for doc, metadata, distance, doc_id in zip(
                    response["documents"][0], response["metadatas"][0],
                    response["distances"][0], response["ids"][0]):
                results.append({"id": doc_id, "source": metadata.get("source", "desconocido"),
                                "source_type": kind, "text": doc,
                                "score": round(max(0.0, 1.0 - float(distance)), 4),
                                "page": metadata.get("page"),
                                "language": metadata.get("language"),
                                "work_order_id": metadata.get("work_order_id"),
                                "equipment_id": metadata.get("equipment_id")})
        return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]

    def status(self):
        def counts(collection):
            sources = set()
            offset = 0
            batch_size = 1000
            total = collection.count()
            while offset < total:
                page = collection.get(limit=batch_size, offset=offset, include=["metadatas"])
                sources.update(item.get("source", "") for item in page["metadatas"] if item)
                offset += batch_size
            sources.discard("")
            return {"documents": len(sources), "chunks": total}

        manuals = counts(self.manuals)
        orders = counts(self.work_orders)
        return {
            "manual_documents": manuals["documents"],
            "manual_chunks": manuals["chunks"],
            "work_order_documents": orders["documents"],
            "work_order_chunks": orders["chunks"],
            "total_documents": manuals["documents"] + orders["documents"],
            "total_chunks": manuals["chunks"] + orders["chunks"],
        }


_store: VectorStore | None = None


def get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
