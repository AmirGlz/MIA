from app.documents import PageText


def chunk_pages(pages: list[PageText], size: int = 300,
                overlap: int = 60) -> list[tuple[str, int | None, int, str | None]]:
    """Divide cada página en ventanas de palabras con solapamiento."""
    if size <= overlap:
        raise ValueError("El tamaño del fragmento debe ser mayor que el solapamiento.")
    chunks: list[tuple[str, int | None, int, str | None]] = []
    for page in pages:
        words = page.text.split()
        start = 0
        while start < len(words):
            end = min(start + size, len(words))
            text = " ".join(words[start:end]).strip()
            if text:
                chunks.append((text, page.page, len(chunks), page.language))
            if end == len(words):
                break
            start = end - overlap
    return chunks
