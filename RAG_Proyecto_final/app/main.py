from contextlib import asynccontextmanager
import logging
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.config import get_settings
from app.rag import RAGService
from app.store import get_store


def _configure_app_logger() -> logging.Logger:
    logger = logging.getLogger("rag.api")
    if not logger.handlers:
        log_file = get_settings().ingestion_log_file
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z"
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


@asynccontextmanager
async def lifespan(_app: FastAPI):
    get_store()
    yield


app = FastAPI(title="RAG de mantenimiento", version="1.0.0", lifespan=lifespan)


class QueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=10)
    source_type: str | None = Field(default=None, pattern="^(manual|work_order)$")
    equipment_id: str | None = None


class PlanRequest(BaseModel):
    equipment_id: str = Field(min_length=2, max_length=100)
    top_k: int | None = Field(default=None, ge=1, le=10)


def service_or_503():
    try:
        return RAGService()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/health")
def health():
    settings = get_settings()
    return {
        "status": "ok",
        "google_api_key_configured": bool(settings.google_api_key),
        "models": {"embedding": settings.google_embedding_model,
                   "generation": settings.google_generation_model},
        "chunking": {"size_words": settings.chunk_size_words,
                     "overlap_words": settings.chunk_overlap_words},
        "ingestion": {"max_upload_size_mb": settings.max_upload_size_mb},
        "abstention": {"minimum_relevance_score": settings.min_relevance_score},
        "index": get_store().status(),
    }


@app.post("/ingest")
async def ingest(files: list[UploadFile] = File(...),
                 source_type: str = Form(...), equipment_id: str | None = Form(default=None)):
    if source_type not in {"manual", "work_order"}:
        raise HTTPException(422, "source_type debe ser 'manual' o 'work_order'.")
    service = service_or_503()
    logger = _configure_app_logger()
    results, errors = [], []
    total_chunks = 0
    for file in files:
        try:
            content = await file.read()
            maximum_bytes = get_settings().max_upload_size_mb * 1024 * 1024
            if len(content) > maximum_bytes:
                raise ValueError(f"El archivo supera el límite de {get_settings().max_upload_size_mb} MB.")
            result = service.ingest(file.filename or "documento", content, source_type, equipment_id)
            results.append(result)
            total_chunks += result["chunks_indexed"]
            logger.info("ingestion_succeeded filename=%r source_type=%s bytes=%d chunks=%d",
                        file.filename, source_type, len(content), result["chunks_indexed"])
        except Exception as exc:
            logger.exception("ingestion_failed filename=%r source_type=%s", file.filename, source_type)
            errors.append({"filename": file.filename, "error": str(exc)})
    if not results:
        raise HTTPException(422, {"message": "No se pudo indexar ningún archivo.", "errors": errors})
    return {"documents_indexed": len(results), "chunks_indexed": total_chunks,
            "files": results, "errors": errors, "index": get_store().status()}


@app.post("/query")
def query(request: QueryRequest):
    try:
        return service_or_503().query(request.question.strip(), request.top_k or get_settings().default_top_k,
                                      request.source_type, request.equipment_id)
    except HTTPException:
        raise
    except Exception as exc:
        _configure_app_logger().exception("query_failed")
        raise HTTPException(502, f"Falló la consulta al proveedor de IA: {exc}") from exc


@app.post("/maintenance-plan")
def maintenance_plan(request: PlanRequest):
    try:
        return service_or_503().maintenance_plan(request.equipment_id.strip(),
                                                 request.top_k or get_settings().default_top_k)
    except HTTPException:
        raise
    except Exception as exc:
        _configure_app_logger().exception("maintenance_plan_failed equipment_id=%r", request.equipment_id)
        raise HTTPException(502, f"No se pudo generar el plan: {exc}") from exc
