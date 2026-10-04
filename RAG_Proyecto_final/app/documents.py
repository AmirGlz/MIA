from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

SUPPORTED_SUFFIXES = {".pdf", ".md", ".txt"}


@dataclass
class PageText:
    text: str
    page: int | None = None
    language: str | None = None


def detect_language(text: str) -> str:
    """Lightweight language hint for source metadata; never used as a filter."""
    sample = f" {text[:5000].lower()} "
    if any(mark in sample for mark in ("¿", "¡", "á", "é", "í", "ó", "ú", "ñ")):
        return "es"
    spanish_markers = (" el ", " la ", " de ", " que ", " para ", " los ", " una ",
                       " operación ", " mantenimiento ", " página ")
    english_markers = (" the ", " and ", " of ", " to ", " for ", " with ", " this ",
                       " maintenance ", " troubleshooting ", " page ")
    es = sum(sample.count(marker) for marker in spanish_markers)
    en = sum(sample.count(marker) for marker in english_markers)
    if es == en == 0:
        return "unknown"
    return "es" if es > en else "en"


def extract_pages(filename: str, content: bytes) -> list[PageText]:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError("Formato no admitido. Sube archivos PDF, Markdown o TXT.")
    if suffix == ".pdf":
        try:
            reader = PdfReader(BytesIO(content))
            pages = [PageText((page.extract_text() or "").strip(), index)
                     for index, page in enumerate(reader.pages, start=1)]
        except Exception as exc:
            raise ValueError(f"No se pudo leer el PDF: {exc}") from exc
        if not any(page.text for page in pages):
            raise ValueError("El PDF no contiene texto extraíble. Los PDF escaneados requieren OCR.")
        return [PageText(page.text, page.page, detect_language(page.text))
                for page in pages if page.text]
    try:
        text = content.decode("utf-8-sig").strip()
    except UnicodeDecodeError as exc:
        raise ValueError("El archivo de texto debe estar codificado en UTF-8.") from exc
    if not text:
        raise ValueError("El documento está vacío.")
    return [PageText(text, language=detect_language(text))]
