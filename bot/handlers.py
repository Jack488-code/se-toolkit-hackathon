"""
Telegram bot handlers — transport layer.

All business logic is delegated to `bot.service`.
Supports Russian (ru) and English (en) languages.
"""

import logging
from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from bot.service import service

logger = logging.getLogger(__name__)

router = Router()

# ── Localizations ──────────────────────────────────────────────────
LANG = {
    "ru": {
        "start": (
            "👋 Привет! Я <b>Flashcard Bot</b>.\n\n"
            "📚 <b>Команды:</b>\n"
            "/add — создать колоду из терминов\n"
            "/decks — список колод\n"
            "/study — начать изучение\n"
            "/help — справка"
        ),
        "add_title": "Введи <b>название</b> новой колоды (например: 'Экзамен по биологии'):",
        "add_terms": (
            "Колода: <b>{title}</b>\n\n"
            "Теперь отправь термины с определениями (каждый с новой строки):\n\n"
            "Формат: <b>термин - определение</b>\n\n"
            "Пример:\n"
            "Митохондрия — органелла клетки, вырабатывающая энергию\n"
            "Рибосома — органелла, синтезирующая белки\n"
            "Ядро — содержит ДНК клетки\n\n"
            "Минимум 2 термина."
        ),
        "add_terms_en": (
            "Deck: <b>{title}</b>\n\n"
            "Now send terms with definitions (one per line):\n\n"
            "Format: <b>term - definition</b>\n\n"
            "Example:\n"
            "Mitochondria — organelle that produces energy\n"
            "Ribosome — organelle that synthesizes proteins\n\n"
            "Minimum 2 terms."
        ),
        "min_terms": "Нужно минимум 2 термина. Попробуй снова:",
        "creating": "⏳ Генерирую карточки...",
        "deck_created": "✅ Колода <b>{title}</b> создана!\n📇 Карточек: {count}\n\nНачни изучение через /study",
        "create_error": "❌ Ошибка при создании колоды.",
        "no_decks": "У тебя пока нет колод. Создай первую через /add",
        "list_decks": "📚 <b>Твои колоды:</b>\n\n{text}",
        "select_deck": "Выбери колоду для изучения:\n\n{text}\n\nОтправь номер колоды:",
        "list_error": "❌ Ошибка при получении списка колод.",
        "select_deck_number": "Отправь номер колоды (число):",
        "no_cards": "🎉 Все карточки изучены! Нет карточек для повторения прямо сейчас.",
        "study_card": "📇 <b>Карточка {current}/{total}</b>\n\n❓ {question}\n\nОценка (0-5):\n0-2 — не знал\n3-4 — вспомнил с трудом\n5 — знал отлично",
        "rating_invalid": "Оценка от 0 до 5 (или задайте вопрос агенту):",
        "not_a_number": "Оценка от 0 до 5:",
        "agent_thinking": "🤖 Думаю...",
        "agent_answer": "🤖 <b>AI-агент о \"{term}\":</b>\n\n{answer}",
        "agent_error": "❌ Ошибка при обращении к агенту.",
        "correct": "✅",
        "incorrect": "❌",
        "answer_reveal": "{emoji} <b>Ответ:</b>\n\n📌 {term}\n💡 {answer}\n\nИнтервал: {interval} дн.",
        "session_done": "🎉 Сессия завершена! Все карточки пройдены.\nНачни новую сессию через /study",
        "help": (
            "📖 <b>Flashcard Bot</b> — умные карточки для подготовки к экзаменам.\n\n"
            "/add — создать колоду из терминов\n"
            "/decks — список колод\n"
            "/study — начать изучение\n"
            "/help — эта справка"
        ),
        "commands_hint": "Используй команды:\n/add — создать колоду\n/decks — список колод\n/study — изучение",
        "lang_select": "🌍 Выберите язык / Select language:",
        "lang_set_ru": "🇷🇺 Язык: русский",
        "lang_set_en": "🇬🇧 Language: English",
        "lang_ru": "🇷🇺 Русский",
        "lang_en": "🇬🇧 English",
        "deck_item": "{i}. <b>{title}</b> — {count} карточек",
        "deck_item_en": "{i}. <b>{title}</b> — {count} cards",
        "study_select": "Выбери колоду:\n\n{text}\n\nОтправь номер:",
        "study_select_en": "Select a deck:\n\n{text}\n\nSend the number:",
    },
    "en": {
        "start": (
            "👋 Hi! I'm <b>Flashcard Bot</b>.\n\n"
            "📚 <b>Commands:</b>\n"
            "/add — create a deck from terms\n"
            "/decks — list your decks\n"
            "/study — start studying\n"
            "/help — help"
        ),
        "add_title": "Enter the <b>deck title</b> (e.g. 'Biology Exam'):",
        "add_terms": "Deck: <b>{title}</b>\n\nNow send the <b>terms</b> (one per line).\nMinimum 2 terms.",
        "min_terms": "Need at least 2 terms. Try again:",
        "creating": "⏳ Generating flashcards...",
        "deck_created": "✅ Deck <b>{title}</b> created!\n📇 Cards: {count}\n\nStart studying via /study",
        "create_error": "❌ Error creating deck.",
        "no_decks": "You don't have any decks yet. Create one via /add",
        "list_decks": "📚 <b>Your decks:</b>\n\n{text}",
        "select_deck": "Select a deck to study:\n\n{text}\n\nSend the deck number:",
        "list_error": "❌ Error listing decks.",
        "select_deck_number": "Send the deck number:",
        "no_cards": "🎉 All cards studied! No cards due for review right now.",
        "study_card": "📇 <b>Card {current}/{total}</b>\n\n❓ {question}\n\nRate your answer (0-5):\n0-2 — didn't know\n3-4 — recalled with difficulty\n5 — knew perfectly",
        "rating_invalid": "Rate 0-5 (or ask the agent a question):",
        "not_a_number": "Send a number from 0 to 5:",
        "agent_thinking": "🤖 Thinking...",
        "agent_answer": "🤖 <b>AI agent on \"{term}\":</b>\n\n{answer}",
        "agent_error": "❌ Error contacting the agent.",
        "correct": "✅",
        "incorrect": "❌",
        "answer_reveal": "{emoji} <b>Answer:</b>\n\n📌 {term}\n💡 {answer}\n\nInterval: {interval} days",
        "session_done": "🎉 Session complete! All cards reviewed.\nStart a new session via /study",
        "help": (
            "📖 <b>Flashcard Bot</b> — smart flashcards for exam prep.\n\n"
            "/add — create a deck from terms\n"
            "/decks — list your decks\n"
            "/study — start studying\n"
            "/help — this help"
        ),
        "commands_hint": "Use commands:\n/add — create a deck\n/decks — list decks\n/study — study",
        "lang_select": "🌍 Select language / Выберите язык:",
        "lang_set_ru": "🇷🇺 Язык: русский",
        "lang_set_en": "🇬🇧 Language: English",
        "lang_ru": "🇷🇺 Русский",
        "lang_en": "🇬🇧 English",
        "deck_item": "{i}. <b>{title}</b> — {count} cards",
        "deck_item_en": "{i}. <b>{title}</b> — {count} cards",
        "study_select": "Select a deck:\n\n{text}\n\nSend the number:",
        "study_select_en": "Select a deck:\n\n{text}\n\nSend the number:",
    },
}


def t(lang: str, key: str) -> str:
    """Get translation string."""
    return LANG.get(lang, LANG["ru"]).get(key, LANG["ru"][key])


def t_fmt(lang: str, key: str, **kwargs) -> str:
    """Get translation and format with kwargs."""
    return t(lang, key).format(**kwargs)


# ── Session state ──────────────────────────────────────────────────
user_states: dict[int, dict] = {}


def get_lang(user_id: int) -> str:
    """Get user's language, default to Russian."""
    return user_states.get(user_id, {}).get("lang", "ru")


# ── Inline keyboards ──────────────────────────────────────────────
def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en")],
    ])


@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)

    # Ensure user is registered
    try:
        await service.register_user(user_id, message.from_user.username)
    except Exception:
        pass

    # Show language selection
    user_states.setdefault(user_id, {})["lang"] = lang
    await message.answer(
        t(lang, "lang_select"),
        reply_markup=lang_keyboard(),
    )


@router.message(Command("lang"))
async def cmd_lang(message: Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    await message.answer(
        t(lang, "lang_select"),
        reply_markup=lang_keyboard(),
    )


@router.callback_query(lambda c: c.data and c.data.startswith("lang:"))
async def handle_lang_selection(callback):
    lang = callback.data.split(":")[1]
    user_id = callback.from_user.id
    user_states.setdefault(user_id, {})["lang"] = lang

    await callback.message.edit_text(t(lang, f"lang_set_{lang}"))

    # Re-show the start message in the selected language
    try:
        await service.register_user(user_id, callback.from_user.username)
    except Exception:
        pass

    await callback.message.answer(t(lang, "start"))


@router.message(Command("add"))
async def cmd_add(message: Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)

    user_states[user_id] = {"state": "waiting_title", "lang": lang}
    await message.answer(t(lang, "add_title"))


@router.message(Command("decks"))
async def cmd_decks(message: Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)

    try:
        decks = await service.list_decks(user_id)
    except Exception as e:
        logger.exception("Error listing decks")
        await message.answer(t(lang, "list_error"))
        return

    if not decks:
        await message.answer(t(lang, "no_decks"))
        return

    item_key = "deck_item"
    items = [
        t_fmt(lang, item_key, i=i, title=d["title"], count=d["card_count"])
        for i, d in enumerate(decks, 1)
    ]
    await message.answer(t_fmt(lang, "list_decks", text="\n".join(items)))


@router.message(Command("study"))
async def cmd_study(message: Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)

    try:
        decks = await service.list_decks(user_id)
    except Exception as e:
        logger.exception("Error listing decks")
        await message.answer(t(lang, "list_error"))
        return

    if not decks:
        await message.answer(t(lang, "no_decks"))
        return

    item_key = "deck_item"
    items = [
        t_fmt(lang, item_key, i=i, title=d["title"], count=d["card_count"])
        for i, d in enumerate(decks, 1)
    ]
    text = "\n".join(items)
    user_states[user_id] = {
        "state": "selecting_deck_for_study",
        "decks": decks,
        "lang": lang,
    }
    await message.answer(t_fmt(lang, "select_deck", text=text))


@router.message(Command("help"))
async def cmd_help(message: Message):
    lang = get_lang(message.from_user.id)
    await message.answer(t(lang, "help"))


@router.message()
async def handle_message(message: Message):
    """Catch-all for conversation flow."""
    user_id = message.from_user.id
    lang = get_lang(user_id)
    state = user_states.get(user_id, {})

    current_state = state.get("state")

    if current_state == "waiting_title":
        state["title"] = message.text
        state["state"] = "waiting_terms"
        state["lang"] = lang
        user_states[user_id] = state
        term_key = "add_terms_en" if lang == "en" else "add_terms"
        await message.answer(t_fmt(lang, term_key, title=message.text))
        return

    if current_state == "waiting_terms":
        terms = [t.strip() for t in message.text.split("\n") if t.strip()]
        if len(terms) < 2:
            await message.answer(t(lang, "min_terms"))
            return

        await message.answer(t(lang, "creating"))
        try:
            deck = await service.create_deck(user_id, state["title"], terms)
        except Exception as e:
            logger.exception("Error creating deck")
            await message.answer(t(lang, "create_error"))
            return

        user_states[user_id] = {"lang": lang}
        await message.answer(
            t_fmt(lang, "deck_created", title=deck["title"], count=deck["card_count"])
        )
        return

    if current_state == "selecting_deck_for_study":
        try:
            idx = int(message.text) - 1
            decks = state["decks"]
            if idx < 0 or idx >= len(decks):
                await message.answer(t(lang, "select_deck_number"))
                return

            deck = decks[idx]
            state["deck_id"] = deck["id"]
            state["state"] = "studying"
            state["lang"] = lang
            user_states[user_id] = state

            cards = await service.start_study(deck["id"], user_id)
            if not cards:
                user_states[user_id] = {"lang": lang}
                await message.answer(t(lang, "no_cards"))
                return

            state["cards"] = cards
            state["current_card_idx"] = 0
            user_states[user_id] = state

            card = cards[0]
            await message.answer(
                t_fmt(lang, "study_card", current=1, total=len(cards), question=card["question"])
            )
            return
        except ValueError:
            await message.answer(t(lang, "select_deck_number"))
            return

    if current_state == "studying":
        # Check if it's a number (rating) or a question for the agent
        try:
            rating = int(message.text)
            if rating < 0 or rating > 5:
                await message.answer(t(lang, "rating_invalid"))
                return
        except ValueError:
            # Not a number — treat as a question for the AI agent
            cards = state.get("cards", [])
            idx = state.get("current_card_idx", 0)
            if idx < len(cards):
                card = cards[idx]
                await message.answer(t(lang, "agent_thinking"))
                try:
                    result = await service.chat(card["id"], message.text)
                    await message.answer(
                        t_fmt(lang, "agent_answer", term=result["term"], answer=result["answer"])
                    )
                except Exception as e:
                    logger.exception("Chat error")
                    await message.answer(t(lang, "agent_error"))
                return
            else:
                await message.answer(t(lang, "not_a_number"))
                return

        # It's a valid rating — submit answer
        cards = state.get("cards", [])
        idx = state.get("current_card_idx", 0)
        card = cards[idx]
        deck_id = state["deck_id"]

        result = await service.submit_answer(deck_id, card["id"], rating, user_id)

        correct_emoji = t(lang, "correct") if result["was_correct"] else t(lang, "incorrect")

        # Show the answer
        await message.answer(
            t_fmt(
                lang,
                "answer_reveal",
                emoji=correct_emoji,
                term=card["term"],
                answer=card.get("definition", "См. определение"),
                interval=result["interval"],
            )
        )

        idx += 1
        if idx >= len(cards):
            user_states[user_id] = {"lang": lang}
            await message.answer(t(lang, "session_done"))
            return

        state["current_card_idx"] = idx
        user_states[user_id] = state
        next_card = cards[idx]
        await message.answer(
            t_fmt(lang, "study_card", current=idx + 1, total=len(cards), question=next_card["question"])
        )
        return

    # Default fallback
    await message.answer(t(lang, "commands_hint"))
