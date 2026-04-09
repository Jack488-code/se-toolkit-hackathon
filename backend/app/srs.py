"""SM-2 spaced repetition algorithm implementation."""

from datetime import datetime, timedelta


def compute_sm2(
    quality: int,
    ease_factor: float = 2.5,
    interval: int = 0,
    repetitions: int = 0,
) -> tuple[float, int]:
    """
    Compute new ease_factor and interval using the SM-2 algorithm.

    Args:
        quality: 0-5 rating of how well the answer was known
        ease_factor: current ease factor (default 2.5)
        interval: current interval in days
        repetitions: number of successful repetitions

    Returns:
        (new_ease_factor, new_interval)
    """
    quality = max(0, min(5, quality))

    if quality < 3:
        # Failed — reset repetitions
        return ease_factor, 0

    # Update ease factor
    new_ef = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ef = max(1.3, new_ef)

    # Update interval
    if repetitions == 0:
        new_interval = 1
    elif repetitions == 1:
        new_interval = 6
    else:
        new_interval = round(interval * new_ef)

    return new_ef, new_interval


def next_review_date(interval: int) -> datetime | None:
    """Compute the next review date from now based on interval in days."""
    if interval <= 0:
        return None
    return datetime.now() + timedelta(days=interval)
