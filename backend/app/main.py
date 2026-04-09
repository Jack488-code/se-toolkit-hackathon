"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import router as api_router
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Flashcard Bot API",
    description="Backend API for the Flashcard Bot — spaced repetition flashcard learning",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
