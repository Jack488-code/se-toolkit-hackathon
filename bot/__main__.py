"""
Telegram bot entry point.

Usage:
    python -m bot              — run the Telegram bot
    python -m bot --test       — CLI test mode (no Telegram)
"""

import argparse
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from bot.config import settings
from bot.handlers import router as handlers_router


async def run_bot():
    dp = Dispatcher()
    dp.include_router(handlers_router)

    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    print("🤖 Flashcard Bot starting...")
    await dp.start_polling(bot)


def cli_test():
    """CLI test mode — exercise business logic without Telegram."""
    from bot.service import service

    async def _test():
        print("🧪 CLI Test Mode")
        print("Registering test user...")
        user = await service.register_user(999999, "cli_test_user")
        print(f"✅ User: {user}")

        print("\nCreating a test deck...")
        deck = await service.create_deck(
            999999, "Test Deck", ["HTTP", "REST API", "WebSocket"]
        )
        print(f"✅ Deck: {deck}")

        print("\nFetching study cards...")
        cards = await service.start_study(deck["id"], 999999)
        print(f"📇 Got {len(cards)} cards:")
        for c in cards:
            print(f"  - {c['question']}")

        if cards:
            print("\nSubmitting answer for first card (rating: 4)...")
            result = await service.submit_answer(deck["id"], cards[0]["id"], 4, 999999)
            print(f"✅ Result: {result}")

    asyncio.run(_test())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Run CLI test mode")
    args = parser.parse_args()

    if args.test:
        cli_test()
    else:
        asyncio.run(run_bot())


if __name__ == "__main__":
    main()
