# Flashcard Bot — Presentation

---

## Slide 1 — Title

**Flashcard Bot**

- **Name:** Sapayev Abdugaffar
- **Email:** a.sapayev@innopoli.university
- **Group:** DSAI-4

---

## Slide 2 — Context

- **End-user:** Students preparing for exams
- **Problem:** Students waste time on rote memorization — paper flashcards are inefficient and there's no optimal review scheduling
- **Product idea:** A Telegram bot that turns a list of terms into smart flashcards and teaches them using spaced repetition (SRS)

---

## Slide 3 — Implementation

**How we built it:**
- **Backend:** FastAPI (Python) + PostgreSQL for data persistence
- **Bot:** aiogram (Telegram transport, separated from business logic)
- **LLM:** OpenRouter API (Qwen model) — fallback to local generation if unavailable
- **SRS:** SM-2 spaced repetition algorithm for optimal review scheduling
- **Deployment:** Docker Compose (backend + bot + PostgreSQL)

**Version 1:**
- User registration, deck creation from terms with definitions, basic study sessions
- SRS study sessions with SM-2 algorithm
- Russian and English language support

**Version 2:**
- AI agent for card explanations during study sessions
- LLM-powered flashcard generation (OpenRouter/Qwen) with fallback
- Docker Compose deployment, CLI test mode
- Improved card retry logic for failed reviews

**TA feedback addressed:**
- Language support: added Russian/English language selection
- Card format: user provides own definitions (term - definition) for reliable content
- Repeated reviews: fixed SRS logic to retry failed cards immediately

---

## Slide 4 — Demo

> **Replace this with a pre-recorded video (max 2 minutes) with voice commentary.**

**Demo script:**
1. Open Telegram → Flashcard Bot → select language
2. `/add` → create deck "Биология" with terms:
   - `Митохондрия — органелла клетки, вырабатывающая энергию`
   - `Рибосома — органелла, синтезирующая белки`
3. Bot creates flashcards with questions
4. `/study` → answer cards, rate 0-5
5. During study, ask the agent a question (type text instead of rating)
6. Show repeated study session — failed cards appear again

---

## Slide 5 — Links

| Resource | Link | QR Code |
|---|---|---|
| GitHub Repo | https://github.com/Jack488-code/se-toolkit-hackathon | Generate QR |
| Deployed Bot | [t.me/flashcrdbot](https://t.me/flashcrdbot) | Generate QR |

> **Generate QR codes at:** https://www.qr-code-generator.com/
