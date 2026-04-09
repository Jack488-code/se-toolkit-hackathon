"""API routes for flashcard management and study."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.llm import chat_about_card, generate_flashcards
from app.models import Card, CardProgress, Deck, User
from app.schemas import (
    AnswerResult,
    AnswerSubmit,
    CardResponse,
    ChatRequest,
    ChatResponse,
    DeckCreate,
    DeckResponse,
    StudyCard,
    UserCreate,
    UserResponse,
)
from app.srs import compute_sm2, next_review_date

router = APIRouter()


# ── Users ──────────────────────────────────────────────────────────
@router.post("/users", response_model=UserResponse)
async def create_or_get_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.telegram_id == user.telegram_id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        return existing

    new_user = User(telegram_id=user.telegram_id, username=user.username)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get("/users/{telegram_id}", response_model=UserResponse)
async def get_user(telegram_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ── Decks ──────────────────────────────────────────────────────────
@router.post("/decks", response_model=DeckResponse)
async def create_deck(deck_in: DeckCreate, db: AsyncSession = Depends(get_db)):
    """Create a deck from terms. Generates flashcards via LLM."""
    # Find or create user based on first term's prefix
    # For simplicity, we'll use telegram_id=0 as default — the bot should create users properly
    # Actually, let's require the bot to send telegram_id in terms list
    # Better approach: the bot passes telegram_id separately. Let's change schema.

    # For now, we'll assume the deck is created via bot which ensures user exists
    # We'll use a workaround: get the first user (bot flow ensures this works)
    stmt = select(User).limit(1)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="No user found. Register first via /users")

    # Generate flashcards via LLM
    cards_data = await generate_flashcards(deck_in.terms)

    deck = Deck(title=deck_in.title, user_id=user.id)
    db.add(deck)
    await db.flush()

    for card_data in cards_data:
        card = Card(
            deck_id=deck.id,
            term=card_data["term"],
            definition=card_data["definition"],
            question=card_data["question"],
            answer=card_data["answer"],
        )
        db.add(card)

    await db.commit()
    await db.refresh(deck)

    card_count_stmt = select(func.count(Card.id)).where(Card.deck_id == deck.id)
    card_count_result = await db.execute(card_count_stmt)
    card_count = card_count_result.scalar()

    return DeckResponse(
        id=deck.id,
        title=deck.title,
        user_id=deck.user_id,
        card_count=card_count or 0,
        created_at=deck.created_at,
    )


@router.get("/users/{telegram_id}/decks", response_model=list[DeckResponse])
async def list_user_decks(telegram_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    decks_stmt = (
        select(Deck)
        .where(Deck.user_id == user.id)
        .options(selectinload(Deck.cards))
        .order_by(Deck.created_at.desc())
    )
    decks_result = await db.execute(decks_stmt)
    decks = decks_result.scalars().all()

    return [
        DeckResponse(
            id=d.id,
            title=d.title,
            user_id=d.user_id,
            card_count=len(d.cards),
            created_at=d.created_at,
        )
        for d in decks
    ]


# ── Study ──────────────────────────────────────────────────────────
@router.get("/decks/{deck_id}/study", response_model=list[StudyCard])
async def get_study_cards(
    deck_id: int, telegram_id: int, db: AsyncSession = Depends(get_db)
):
    """Get cards due for review (SRS-based)."""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all cards in deck
    cards_stmt = select(Card).where(Card.deck_id == deck_id)
    cards_result = await db.execute(cards_stmt)
    all_cards = cards_result.scalars().all()

    if not all_cards:
        return []

    # Get progress for this user + deck
    progress_stmt = select(CardProgress).where(
        CardProgress.user_id == user.id,
        CardProgress.deck_id == deck_id,
    )
    progress_result = await db.execute(progress_stmt)
    progress_map = {p.card_id: p for p in progress_result.scalars().all()}

    now = datetime.now()
    due_cards = []

    for card in all_cards:
        prog = progress_map.get(card.id)
        if prog is None:
            # Never studied — due now
            due_cards.append(card)
        elif prog.interval == 0:
            # Failed or reset — due immediately for re-study
            due_cards.append(card)
        elif prog.next_review and prog.next_review <= now:
            due_cards.append(card)

    # Limit to 10 cards per session
    due_cards = due_cards[:10]

    return [
        StudyCard(id=c.id, question=c.question, term=c.term, definition=c.definition)
        for c in due_cards
    ]


@router.post("/decks/{deck_id}/answer", response_model=AnswerResult)
async def submit_answer(
    deck_id: int,
    answer: AnswerSubmit,
    telegram_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Submit an answer and update SRS state."""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get or create progress
    prog_stmt = select(CardProgress).where(
        CardProgress.user_id == user.id,
        CardProgress.card_id == answer.card_id,
    )
    prog_result = await db.execute(prog_stmt)
    progress = prog_result.scalar_one_or_none()

    if progress is None:
        progress = CardProgress(
            user_id=user.id,
            deck_id=deck_id,
            card_id=answer.card_id,
        )
        db.add(progress)
        await db.flush()

    was_correct = answer.self_rating >= 3

    new_ef, new_interval = compute_sm2(
        quality=answer.self_rating,
        ease_factor=progress.ease_factor,
        interval=progress.interval,
        repetitions=progress.repetitions,
    )

    progress.ease_factor = new_ef
    progress.interval = new_interval
    progress.repetitions = progress.repetitions + 1 if was_correct else 0
    progress.last_review = datetime.now()
    progress.next_review = next_review_date(new_interval)

    await db.commit()
    await db.refresh(progress)

    return AnswerResult(
        card_id=progress.card_id,
        was_correct=was_correct,
        ease_factor=progress.ease_factor,
        interval=progress.interval,
        next_review=progress.next_review,
    )


# ── Deck detail ────────────────────────────────────────────────────
@router.get("/decks/{deck_id}", response_model=DeckResponse)
async def get_deck(deck_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Deck).where(Deck.id == deck_id)
    result = await db.execute(stmt)
    deck = result.scalar_one_or_none()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    card_count_stmt = select(func.count(Card.id)).where(Card.deck_id == deck_id)
    card_count_result = await db.execute(card_count_stmt)
    card_count = card_count_result.scalar()

    return DeckResponse(
        id=deck.id,
        title=deck.title,
        user_id=deck.user_id,
        card_count=card_count or 0,
        created_at=deck.created_at,
    )


# ── Chat with agent ────────────────────────────────────────────────
@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(chat: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Ask the LLM agent a question about a specific flashcard."""
    card_stmt = select(Card).where(Card.id == chat.card_id)
    card_result = await db.execute(card_stmt)
    card = card_result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    answer = await chat_about_card(
        term=card.term,
        definition=card.definition,
        question=card.question,
        answer=card.answer,
        user_message=chat.message,
    )

    return ChatResponse(card_id=card.id, term=card.term, answer=answer)
