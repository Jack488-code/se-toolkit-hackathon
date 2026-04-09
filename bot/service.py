"""
Business logic for the Flashcard Bot.

This module is completely independent of Telegram transport
and can be tested via CLI or unit tests.
"""

from bot.api_client import backend


class FlashcardService:
    """Core business logic — independent of transport."""

    async def register_user(self, telegram_id: int, username: str | None = None) -> dict:
        return await backend.create_user(telegram_id, username)

    async def list_decks(self, telegram_id: int) -> list[dict]:
        return await backend.list_decks(telegram_id)

    async def create_deck(
        self, telegram_id: int, title: str, terms: list[str]
    ) -> dict:
        return await backend.create_deck(telegram_id, title, terms)

    async def start_study(self, deck_id: int, telegram_id: int) -> list[dict]:
        return await backend.get_study_cards(deck_id, telegram_id)

    async def submit_answer(
        self, deck_id: int, card_id: int, self_rating: int, telegram_id: int
    ) -> dict:
        return await backend.submit_answer(deck_id, card_id, self_rating, telegram_id)

    async def chat(self, card_id: int, message: str) -> dict:
        return await backend.chat(card_id, message)


service = FlashcardService()
