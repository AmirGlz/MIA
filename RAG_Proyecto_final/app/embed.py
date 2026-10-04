import re
import time

from google import genai
from google.genai.errors import APIError
from google.genai import types


class GoogleAIEmbeddings:
    """Genera vectores para documentos y consultas con el mismo modelo."""

    def __init__(self, client: genai.Client, model: str) -> None:
        self.client = client
        self.model = model

    def embed(self, texts: list[str], task_type: str) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), 50):
            batch = texts[start:start + 50]
            for attempt in range(3):
                try:
                    response = self.client.models.embed_content(
                        model=self.model,
                        contents=batch,
                        config=types.EmbedContentConfig(task_type=task_type, output_dimensionality=768),
                    )
                    break
                except APIError as exc:
                    # Retry only temporary rate limits with an explicit provider delay.
                    # Daily/billing quota errors have no retryDelay and should fail fast.
                    retry_delay = self._retry_delay(exc) if exc.code == 429 else None
                    if retry_delay is None or attempt == 2:
                        raise
                    time.sleep(retry_delay)
            vectors.extend(item.values for item in response.embeddings)
        return vectors

    @staticmethod
    def _retry_delay(exc: APIError) -> float | None:
        for detail in (exc.details.get("error", {}).get("details", [])
                       if isinstance(exc.details, dict) else []):
            if detail.get("@type", "").endswith("google.rpc.RetryInfo"):
                match = re.fullmatch(r"(\d+(?:\.\d+)?)s", detail.get("retryDelay", ""))
                if match:
                    return float(match.group(1)) + 1.0
        return None
