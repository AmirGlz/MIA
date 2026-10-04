from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


class Settings(BaseSettings):
    google_api_key: str = ""
    google_embedding_model: str = "gemini-embedding-001"
    google_generation_model: str = "gemini-3.8-flash"
    chroma_path: str = "./chroma"
    min_relevance_score: float = 0.35
    default_top_k: int = 4
    chunk_size_words: int = 300
    chunk_overlap_words: int = 60
    max_upload_size_mb: int = 75
    ingestion_log_path: str = "./logs/ingestion.log"

    model_config = SettingsConfigDict(env_file=str(ROOT / ".env"), extra="ignore")

    @property
    def chroma_directory(self) -> Path:
        path = Path(self.chroma_path)
        return path if path.is_absolute() else ROOT / path

    @property
    def ingestion_log_file(self) -> Path:
        path = Path(self.ingestion_log_path)
        return path if path.is_absolute() else ROOT / path


@lru_cache
def get_settings() -> Settings:
    return Settings()
