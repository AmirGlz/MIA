import argparse
import re
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "data/example_corpus"
SUPPORTED = {".pdf", ".md", ".txt"}


def extract_word_count(path: Path) -> int:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(BytesIO(path.read_bytes()))
        return sum(len((page.extract_text() or "").split()) for page in reader.pages)
    return len(path.read_text(encoding="utf-8").split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida el tamaño del corpus de ejemplo para RAG.")
    parser.add_argument("--minimum-documents", type=int, default=5)
    parser.add_argument("--minimum-words", type=int, default=3000)
    parser.add_argument("--expected-orders", type=int, default=100)
    args = parser.parse_args()

    groups = {
        "manuals": sorted(path for path in (CORPUS / "manuals").rglob("*")
                           if path.is_file() and path.suffix.lower() in SUPPORTED),
        "work_orders": sorted(path for path in (CORPUS / "work_orders").rglob("*")
                              if path.is_file() and path.suffix.lower() in SUPPORTED),
    }
    files = groups["manuals"] + groups["work_orders"]
    words = 0
    errors = []
    if len(files) < args.minimum_documents:
        errors.append(f"Hay {len(files)} documentos; se requieren {args.minimum_documents}.")
    if not groups["manuals"]:
        errors.append("No hay documentos técnicos en data/example_corpus/manuals/.")
    if not groups["work_orders"]:
        errors.append("No hay PDFs en data/example_corpus/work_orders/.")
    if len(groups["work_orders"]) != args.expected_orders:
        errors.append(f"Hay {len(groups['work_orders'])} órdenes; se esperaban {args.expected_orders}.")
    equipment_counts = {"PRN-HP-01": 0, "CUT-IDEAL-01": 0,
                        "PC-HP-01": 0, "PRN-KODAK-01": 0}
    for path in files:
        try:
            count = extract_word_count(path)
            if count == 0:
                errors.append(f"No se pudo extraer texto de {path.relative_to(ROOT)}.")
            words += count
            if path.parent.name == "work_orders" and path.suffix.lower() == ".pdf":
                reader = PdfReader(BytesIO(path.read_bytes()))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
                if "Orden sintética" not in text:
                    errors.append(f"Falta la marca de orden sintética en {path.name}.")
                match = re.search(r"Equipo\s+([A-Z]+-[A-Z0-9-]+)", text)
                if not match:
                    errors.append(f"No se encontró equipment_id en {path.name}.")
                elif match.group(1) in equipment_counts:
                    equipment_counts[match.group(1)] += 1
                else:
                    errors.append(f"Equipo no aprobado en {path.name}: {match.group(1)}.")
        except Exception as exc:
            errors.append(f"No se pudo leer {path.relative_to(ROOT)}: {exc}")
    if words < args.minimum_words:
        errors.append(f"Hay {words} palabras extraíbles; se requieren {args.minimum_words}.")
    for equipment_id, count in equipment_counts.items():
        if count != 25:
            errors.append(f"{equipment_id}: hay {count} órdenes; se esperaban 25.")
    if errors:
        print("Corpus de ejemplo no válido:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Corpus correcto: {len(groups['manuals'])} guías, {len(groups['work_orders'])} órdenes, "
          f"{len(files)} documentos y {words:,} palabras extraíbles.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
