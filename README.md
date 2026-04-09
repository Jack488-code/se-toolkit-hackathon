# Flashcard Bot

A Telegram bot that turns a list of terms into smart flashcards and teaches them using spaced repetition.

## Product Context

- **End users:** Students preparing for exams who need to memorize terms and definitions efficiently.
- **Problem:** Students waste time on rote memorization with paper flashcards or basic apps that don't optimize review timing.
- **Solution:** The bot auto-generates flashcards from a list of terms (using LLM) and shows them in optimal order via a Spaced Repetition System (SRS, SM-2 algorithm), so students learn faster and retain longer.

## Features

### Implemented (Version 1 & 2)

| Feature | Status |
|---|---|
| User registration via `/start` | ✅ |
| Create deck from terms (`/add`) | ✅ |
| LLM-powered flashcard generation (OpenRouter/Qwen) | ✅ |
| SRS study sessions (`/study`) with SM-2 algorithm | ✅ |
| List decks (`/decks`) | ✅ |
| CLI test mode (`--test`) | ✅ |
| PostgreSQL persistence | ✅ |
| Docker Compose deployment | ✅ |

### Not yet implemented

| Feature | Notes |
|---|---|
| Inline keyboard buttons for rating | Currently uses text input (0-5) |
| Deck deletion and editing | — |
| Study statistics and progress tracking | — |
| Shared/public decks | — |
| Web dashboard | — |

## Usage

### As a Telegram user

1. Open the bot in Telegram
2. Send `/start` to register
3. Send `/add` and follow the prompts:
   - Enter a deck title (e.g. "Biology Final")
   - Enter terms with definitions, one per line: `term - definition`
4. Flashcards are created from your definitions
5. Send `/study` to start a review session
6. Rate each answer 0-5 (how well you knew it)
7. SRS schedules your next review optimally

### Bot commands

| Command | Description |
|---|---|
| `/start` | Register and get help |
| `/add` | Create a new flashcard deck |
| `/decks` | List your decks |
| `/study` | Start a study session |
| `/help` | Show help message |

## Architecture

```
┌─────────────┐       ┌──────────────┐       ┌──────────────┐
│  Telegram   │──────▶│  Telegram    │──────▶│  FastAPI     │
│  User       │◀──────│  Bot (aiogram)│◀──────│  Backend     │
└─────────────┘       └──────────────┘       └──────┬───────┘
                                                    │
                                             ┌──────▼───────┐
                                             │  PostgreSQL  │
                                             └──────────────┘
                                                    ▲
                                             ┌──────┴───────┐
                                             │  OpenRouter  │
                                             │  (LLM API)   │
                                             └──────────────┘
```

**Components:**
- **Backend (FastAPI):** REST API for deck/card management, SRS logic, LLM integration
- **Bot (aiogram):** Telegram transport layer, delegates logic to backend via API
- **Database (PostgreSQL):** Users, decks, cards, SRS progress
- **LLM (OpenRouter/Qwen):** Generates flashcard questions from raw terms

## Deployment

### Requirements

- **OS:** Ubuntu 24.04 (or any Linux with Docker)
- **Installed:** Docker 24+, Docker Compose 2.x
- **Obtained:**
  - Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
  - OpenRouter API Key (optional, from [openrouter.ai](https://openrouter.ai)) — without it, trivial fallback flashcards are generated

### Step-by-step

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Jack488-code/se-toolkit-hackathon.git
   cd se-toolkit-hackathon
   ```

2. **Create `.env` file:**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set:

   ```env
   BOT_TOKEN=your-actual-telegram-token
   OPENROUTER_API_KEY=your-openrouter-key   # optional
   ```

3. **Start all services:**

   ```bash
   docker compose up -d --build
   ```

   This starts:
   - PostgreSQL on internal network
   - Backend on `http://localhost:8000`
   - Telegram bot (polling)

4. **Verify the backend:**

   ```bash
   curl http://localhost:8000/health
   # Expected: {"status": "ok"}
   ```

5. **Test the bot CLI (no Telegram needed):**

   ```bash
   docker compose exec bot python -m bot --test
   ```

6. **View logs:**

   ```bash
   docker compose logs -f bot
   docker compose logs -f backend
   ```

7. **Stop services:**

   ```bash
   docker compose down
   ```

### API Documentation

Once running, visit `http://localhost:8000/docs` for interactive Swagger UI.
