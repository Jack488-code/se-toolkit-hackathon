"""LLM-powered flashcard generation via OpenRouter API."""

import json

import httpx

from app.config import settings


def parse_terms(lines: list[str]) -> list[dict[str, str]]:
    """
    Parse user input into term/definition pairs.
    Format: "Term - Definition" or just "Term".

    Returns list of {"term": ..., "definition": ...}
    """
    cards = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if " - " in line or " — " in line:
            sep = " - " if " - " in line else " — "
            parts = line.split(sep, 1)
            cards.append({"term": parts[0].strip(), "definition": parts[1].strip()})
        else:
            cards.append({"term": line, "definition": ""})
    return cards


async def generate_flashcards(terms: list[str]) -> list[dict[str, str]]:
    """
    Generate flashcard Q&A from user-provided terms/definitions.

    If user provided definitions (format: "Term - Definition"),
    the LLM only needs to generate questions.

    If user provided just terms, LLM generates full flashcards.

    Falls back to local generation if LLM is unavailable.
    """
    parsed = parse_terms(terms)
    has_definitions = any(c["definition"] for c in parsed)

    if has_definitions and (not settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEY.startswith("your-")):
        # User provided definitions, no LLM — create basic Q&A
        return _from_user_definitions(parsed)

    if not has_definitions and (not settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEY.startswith("your-")):
        # No definitions, no LLM — fallback
        return _fallback_flashcards(terms)

    # LLM is available
    return await _llm_generate(parsed, has_definitions)


async def _llm_generate(parsed: list[dict], has_definitions: bool) -> list[dict[str, str]]:
    """Use LLM to generate or enhance flashcards."""
    is_ru = any(_is_cyrillic(c["term"]) for c in parsed)

    if has_definitions:
        # User provided definitions — LLM generates questions
        terms_text = "\n".join(
            f"- {c['term']}: {c['definition']}" for c in parsed
        )
        if is_ru:
            system_prompt = (
                "Ты генератор флеш-карточек. Пользователь дал определения. "
                "Для каждого термина создай:\n"
                "1. question — вопрос, проверяющий знание этого термина\n"
                "2. answer — краткий ответ (перефразируй определение)\n"
                "Используй 'term' и 'definition' из ввода.\n"
                "Отвечай ТОЛЬКО валидным JSON-массивом с ключами: "
                '"term", "definition", "question", "answer". Пиши на русском.'
            )
        else:
            system_prompt = (
                "You are a flashcard generator. The user provided definitions. "
                "For each term, create:\n"
                "1. question — a question that tests knowledge of the term\n"
                "2. answer — a brief answer (rephrase the definition)\n"
                "Use 'term' and 'definition' from input.\n"
                "Respond ONLY with a valid JSON array with keys: "
                '"term", "definition", "question", "answer".'
            )
    else:
        # No definitions — LLM generates everything
        terms_text = "\n".join(f"- {c['term']}" for c in parsed)
        if is_ru:
            system_prompt = (
                "Ты генератор флеш-карточек. Для каждого термина создай:\n"
                "1. definition — короткое точное определение\n"
                "2. question — вопрос, проверяющий знание термина\n"
                "3. answer — ответ на этот вопрос\n"
                "Отвечай ТОЛЬКО валидным JSON-массивом объектов с ключами: "
                '"term", "definition", "question", "answer". Пиши на русском.'
            )
        else:
            system_prompt = (
                "You are a flashcard generator. Given a list of terms, create clear, "
                "concise flashcards. For each term provide:\n"
                "1. definition — a short, precise definition\n"
                "2. question — a question that tests knowledge of the term\n"
                "3. answer — the answer to that question\n"
                "Respond ONLY with a valid JSON array of objects with keys: "
                '"term", "definition", "question", "answer".'
            )

    user_prompt = f"Создай флеш-карточки:\n{terms_text}" if is_ru else f"Generate flashcards:\n{terms_text}"

    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
    }

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/flashcard-bot",
    }

    async with httpx.AsyncClient(timeout=60) as client:
        try:
            resp = await client.post(
                settings.OPENROUTER_API_URL,
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError:
            if has_definitions:
                return _from_user_definitions(parsed)
            return _fallback_flashcards([c["term"] for c in parsed])

    content = data["choices"][0]["message"]["content"].strip()

    if content.startswith("```"):
        content = content.split("\n", 1)[-1]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

    try:
        cards = json.loads(content)
        result = []
        for c in cards:
            result.append({
                "term": c.get("term", ""),
                "definition": c.get("definition", ""),
                "question": c.get("question", ""),
                "answer": c.get("answer", ""),
            })
        return result
    except json.JSONDecodeError:
        if has_definitions:
            return _from_user_definitions(parsed)
        return _fallback_flashcards([c["term"] for c in parsed])


def _from_user_definitions(parsed: list[dict]) -> list[dict[str, str]]:
    """Create flashcards from user-provided term-definition pairs."""
    ru = any(_is_cyrillic(c["term"]) for c in parsed)
    cards = []
    for c in parsed:
        term = c["term"]
        definition = c["definition"] or "Нет определения"
        if ru:
            question = f"Что такое {term}?"
            answer = definition
        else:
            question = f"What is {term}?"
            answer = definition
        cards.append({
            "term": term,
            "definition": definition,
            "question": question,
            "answer": answer,
        })
    return cards


def _is_cyrillic(text: str) -> bool:
    """Check if text contains Cyrillic characters."""
    return any('\u0400' <= c <= '\u04FF' for c in text)


def _fallback_flashcards(terms: list[str]) -> list[dict[str, str]]:
    """Generate basic flashcards without LLM (when no API key)."""
    ru = any(_is_cyrillic(t) for t in terms)

    if ru:
        return [
            {
                "term": term,
                "definition": f"Определение: {term}",
                "question": f"Что такое {term}?",
                "answer": f"См. определение: {term}",
            }
            for term in terms
        ]
    else:
        return [
            {
                "term": term,
                "definition": f"Definition of {term}",
                "question": f"What is {term}?",
                "answer": f"See definition: {term}",
            }
            for term in terms
        ]


async def chat_about_card(
    term: str, definition: str, question: str, answer: str, user_message: str
) -> str:
    """
    LLM agent that answers user questions about a specific flashcard.
    Uses the card's context to provide helpful, educational responses.
    """
    ru = _is_cyrillic(term)

    if not settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEY.startswith("your-"):
        # Fallback: show the card's question and answer
        if ru:
            return (
                f"💡 <b>{term}</b>\n\n"
                f"📝 {question}\n"
                f"📖 {answer}"
            )
        else:
            return (
                f"💡 <b>{term}</b>\n\n"
                f"📝 {question}\n"
                f"📖 {answer}"
            )

    if ru:
        system_prompt = (
            "Ты помощник для учёбы. Объясняй понятия кратко и понятно. "
            "Помогай студентам разбираться в темах флеш-карточек. "
            "Ответы — 2-3 предложения, информативные. Приводи примеры, если полезно."
        )
    else:
        system_prompt = (
            "You are a helpful study assistant. You explain concepts clearly and concisely. "
            "You help students understand flashcard topics. Keep answers short (2-3 sentences) "
            "but informative. Use examples when helpful."
        )

    context = (
        f"Flashcard context:\n"
        f"  Term: {term}\n"
        f"  Definition: {definition}\n"
        f"  Question: {question}\n"
        f"  Answer: {answer}"
    )

    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{context}\n\nUser question: {user_message}"},
        ],
        "temperature": 0.7,
        "max_tokens": 300,
    }

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/flashcard-bot",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.post(
                settings.OPENROUTER_API_URL,
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError:
            return f"📌 <b>{term}</b>: {definition}"

    return data["choices"][0]["message"]["content"].strip()
