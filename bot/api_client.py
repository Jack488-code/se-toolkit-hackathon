"""HTTP client for communicating with the Flashcard Backend API."""

import httpx

from bot.config import settings


class BackendClient:
    """Thin wrapper around the backend API."""

    def __init__(self):
        self.base_url = settings.API_URL

    async def create_user(self, telegram_id: int, username: str | None = None) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/users",
                json={"telegram_id": telegram_id, "username": username},
            )
            resp.raise_for_status()
            return resp.json()

    async def list_decks(self, telegram_id: int) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/users/{telegram_id}/decks")
            resp.raise_for_status()
            return resp.json()

    async def create_deck(self, telegram_id: int, title: str, terms: list[str]) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/decks",
                json={"title": title, "terms": terms},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_study_cards(self, deck_id: int, telegram_id: int) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/decks/{deck_id}/study",
                params={"telegram_id": telegram_id},
            )
            resp.raise_for_status()
            return resp.json()

    async def submit_answer(
        self, deck_id: int, card_id: int, self_rating: int, telegram_id: int
    ) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/decks/{deck_id}/answer",
                params={"telegram_id": telegram_id},
                json={"card_id": card_id, "self_rating": self_rating},
            )
            resp.raise_for_status()
            return resp.json()

    async def chat(self, card_id: int, message: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/chat",
                json={"card_id": card_id, "message": message},
            )
            resp.raise_for_status()
            return resp.json()


backend = BackendClient()
