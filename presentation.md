# Flashcard Bot — Presentation

> Fill in the bracketed fields with your information.

---

## Slide 1 — Title

**Flashcard Bot**

- **Name:** [Your Name]
- **Email:** [your.email@university.edu]
- **Group:** [Your Group]

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
- **LLM:** OpenRouter API (Qwen model) for automatic flashcard generation
- **SRS:** SM-2 spaced repetition algorithm for optimal review scheduling

**Version 1:**
- User registration, deck creation from terms, basic study sessions

**Version 2:**
- LLM-powered flashcard generation, full SM-2 algorithm, Docker Compose deployment, CLI test mode

**TA feedback addressed:**
- [List the specific feedback points from your TA and how you addressed them]

---

## Slide 4 — Demo

> **Replace this with a pre-recorded video (max 2 minutes) with voice commentary.**

**Demo script:**
1. Open Telegram → Flashcard Bot
2. `/start` — registration
3. `/add` — create deck "Biology Final" with terms: Mitochondria, Ribosome, Nucleus, DNA, RNA
4. Bot generates flashcards via LLM
5. `/study` — answer cards, rate 0-5
6. Show SRS scheduling in action

---

## Slide 5 — Links

| Resource | Link | QR Code |
|---|---|---|
| GitHub Repo | `https://github.com/[your-username]/se-toolkit-hackathon` | [QR] |
| Deployed Bot | Telegram: `@[your-bot-username]` | [QR] |
| API Docs | `http://[your-vm-ip]:8000/docs` | [QR] |

> **Generate QR codes at:** https://www.qr-code-generator.com/
