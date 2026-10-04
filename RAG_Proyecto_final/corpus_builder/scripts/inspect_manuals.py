"""Report candidate manual size and chunk cost without calling any AI service."""
import csv
import logging
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from app.chunk import chunk_pages
from app.config import get_settings
from app.documents import PageText, detect_language, extract_pages

SOURCES = ROOT / "corpus_builder/input/manual_sources.csv"


def read_pages(path: Path) -> list[PageText]:
    # Poppler is much faster for the large HP repair PDF; keep pypdf as the
    # portable fallback used by the application itself.
    if shutil.which("pdftotext"):
        result = subprocess.run(["pdftotext", "-enc", "UTF-8", "-layout", str(path), "-"],
                                capture_output=True, text=True, check=False)
        if result.returncode == 0 and result.stdout.strip():
            pages = [text.strip() for text in result.stdout.split("\f") if text.strip()]
            return [PageText(text, index, detect_language(text))
                    for index, text in enumerate(pages, start=1)]
    return extract_pages(path.name, path.read_bytes())


def main() -> int:
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    settings = get_settings()
    rows = []
    with SOURCES.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            paths = [part.strip() for part in row.get("local_path", "").split(";") if part.strip()]
            for raw_path in paths:
                path = ROOT / raw_path
                included = not row.get("index_scope", "").startswith("excluidos del índice")
                if not path.is_file():
                    rows.append((raw_path, "missing", 0, 0, 0, row.get("index_scope", "")))
                    continue
                size = path.stat().st_size
                if not included:
                    rows.append((raw_path, "excluded", size, 0, 0, row.get("index_scope", "")))
                    continue
                try:
                    pages = read_pages(path)
                    chunks = chunk_pages(pages, settings.chunk_size_words, settings.chunk_overlap_words)
                    words = sum(len(page.text.split()) for page in pages)
                    language = ",".join(sorted({page.language or "unknown" for page in pages}))
                    rows.append((raw_path, language, size, len(pages), len(chunks),
                                 f"{words:,} palabras; {row.get('index_scope', '')}"))
                except Exception as exc:
                    rows.append((raw_path, f"error: {exc}", size, 0, 0, row.get("index_scope", "")))

    print("idioma/estado\tbytes\tpáginas\tpalabras/chunks\tarchivo\talcance")
    for path, language, size, pages, chunks, scope in rows:
        words_summary = scope.split(";", 1)[0]
        print(f"{language}\t{size}\t{pages}\t{words_summary} / {chunks}\t{path}\t{scope}")
    included = [row for row in rows if row[1] not in {"excluded", "missing"} and not row[1].startswith("error:")]
    print(f"Fuentes incluidas: {len(included)}; bytes: {sum(row[2] for row in included):,}; "
          f"páginas extraídas: {sum(row[3] for row in included):,}; "
          f"fragmentos estimados: {sum(row[4] for row in included):,}.")
    return 1 if any(row[1] == "missing" or row[1].startswith("error:") for row in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
