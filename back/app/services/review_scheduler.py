from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class ReviewScheduleResult:
    next_review_at: datetime
    memory_level: int


RATING_INTERVALS = {
    "forgot": timedelta(days=1),
    "hard": timedelta(days=3),
    "remembered": timedelta(days=7),
    "mastered": timedelta(days=30),
}

RATING_MEMORY_DELTAS = {
    "forgot": -2,
    "hard": -1,
    "remembered": 1,
    "mastered": 2,
}


def schedule_next_review(
    rating: str,
    *,
    now: datetime,
    memory_level: int,
) -> ReviewScheduleResult:
    if rating not in RATING_INTERVALS:
        allowed = ", ".join(RATING_INTERVALS)
        raise ValueError(f"Unsupported review rating: {rating}. Allowed values: {allowed}")

    next_level = max(0, min(5, memory_level + RATING_MEMORY_DELTAS[rating]))
    return ReviewScheduleResult(
        next_review_at=now + RATING_INTERVALS[rating],
        memory_level=next_level,
    )

