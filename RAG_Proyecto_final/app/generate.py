from google import genai
from google.genai import types


def answer_with_evidence(client: genai.Client, model: str, question: str,
                         citations: list[dict], minimum_score: float) -> tuple[str, bool]:
    useful = [(index, item) for index, item in enumerate(citations, start=1)
              if item["score"] >= minimum_score]
    if not useful:
        return "No tengo evidencia suficiente en los documentos indexados para responder.", True
    context = "\n\n".join(
        f"[{index}] Fuente: {item['source']}" +
        (f", página {item['page']}" if item.get("page") else "") +
        f"\n{item['text']}" for index, item in useful
    )
    prompt = (
        "Responde en español y usa únicamente la evidencia numerada del contexto. "
        "Incluye citas [n] junto a cada afirmación. Si falta evidencia para una parte, "
        "dilo con claridad y no completes con conocimiento externo.\n\n"
        f"Contexto:\n{context}\n\nPregunta: {question}"
    )
    response = client.models.generate_content(
        model=model, contents=prompt,
        config=types.GenerateContentConfig(temperature=0.2),
    )
    text = (response.text or "").strip()
    if not text:
        return "No tengo evidencia suficiente para elaborar una respuesta.", True
    return text, False
