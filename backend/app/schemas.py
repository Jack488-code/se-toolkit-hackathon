from datetime import datetime

from pydantic import BaseModel


# ── Users ──────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    telegram_id: int
    username: str | None = None


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Decks ──────────────────────────────────────────────────────────
class DeckCreate(BaseModel):
    title: str
    terms: list[str]  # raw terms: "Термин - Описание" or just terms for LLM


class DeckResponse(BaseModel):
    id: int
    title: str
    user_id: int
    card_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Cards ──────────────────────────────────────────────────────────
class CardResponse(BaseModel):
    id: int
    deck_id: int
    term: str
    definition: str
    question: str
    answer: str

    model_config = {"from_attributes": True}


# ── Study session ──────────────────────────────────────────────────
class StudyCard(BaseModel):
    """Card returned for study (answer hidden)."""

    id: int
    question: str
    term: str
    definition: str = ""


class AnswerSubmit(BaseModel):
    card_id: int
    self_rating: int  # 0-5: how well user knew the answer (SM-2 quality)


class ChatRequest(BaseModel):
    card_id: int
    message: str


class ChatResponse(BaseModel):
    card_id: int
    term: str
    answer: str


class AnswerResult(BaseModel):
    card_id: int
    was_correct: bool
    ease_factor: float
    interval: int
    next_review: datetime | None


# ── Deck with cards ────────────────────────────────────────────────
class DeckDetail(BaseModel):
    id: int
    title: str
    cards: list[CardResponse]

    model_config = {"from_attributes": True}
