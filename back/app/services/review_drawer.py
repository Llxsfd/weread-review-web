import random
from dataclasses import dataclass
from datetime import datetime

from app.db.models import Book, Highlight, ReviewCard, ReviewLog


@dataclass(frozen=True)
class ReviewCandidate:
    card: ReviewCard
    highlight: Highlight
    book: Book


def filter_review_candidates(
    candidates: list[ReviewCandidate],
    *,
    mode: str,
    book_id: str | None,
    category: str | None,
) -> list[ReviewCandidate]:
    normalized_mode = (mode or "random").strip().lower()
    if normalized_mode == "book" and book_id:
        return [candidate for candidate in candidates if candidate.highlight.book_id == book_id]
    if normalized_mode == "category" and category:
        target = category.strip()
        return [candidate for candidate in candidates if (candidate.book.category or "").strip() == target]
    return candidates


def choose_review_candidate(
    candidates: list[ReviewCandidate],
    *,
    recent_logs: list[ReviewLog],
    now: datetime,
    exclude_book_id: str | None,
) -> ReviewCandidate | None:
    preferred = candidates
    if exclude_book_id:
        non_repeated = [candidate for candidate in candidates if candidate.highlight.book_id != exclude_book_id]
        if non_repeated:
            preferred = non_repeated

    logs_by_card: dict[int, list[ReviewLog]] = {}
    for log in recent_logs:
        logs_by_card.setdefault(log.review_card_id, []).append(log)

    scored = sorted(
        (
            (
                score_review_candidate(candidate.card, logs_by_card.get(candidate.card.id, []), now=now),
                candidate,
            )
            for candidate in preferred
        ),
        key=lambda item: item[0],
        reverse=True,
    )
    if not scored:
        return None
    return scored[0][1]


def score_review_candidate(card: ReviewCard, logs: list[ReviewLog], *, now: datetime) -> float:
    overdue_days = max(0.0, (now - card.next_review_at).total_seconds() / 86400)
    forgot_count = sum(1 for log in logs if log.rating == "forgot")
    hard_count = sum(1 for log in logs if log.rating == "hard")
    remembered_count = sum(1 for log in logs if log.rating in ("remembered", "mastered"))
    days_since_review = (
        max(0.0, (now - card.last_reviewed_at).total_seconds() / 86400) if card.last_reviewed_at else 14.0
    )

    novelty_bonus = 2.4 if card.review_count <= 0 else 0.0
    weakness_bonus = max(0.0, 5 - card.memory_level) * 0.8
    difficulty_bonus = forgot_count * 1.6 + hard_count * 0.9 - remembered_count * 0.35
    recency_bonus = min(3.5, days_since_review / 5)
    overdue_bonus = min(4.0, overdue_days * 1.3)
    revisit_penalty = min(1.6, card.review_count * 0.15)
    jitter = random.random() * 0.35

    return novelty_bonus + weakness_bonus + difficulty_bonus + recency_bonus + overdue_bonus - revisit_penalty + jitter
