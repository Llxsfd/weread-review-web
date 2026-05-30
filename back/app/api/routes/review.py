from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import Book, Highlight, ReviewCard, ReviewLog
from app.db.models import User
from app.db.session import get_db
from app.services.review_drawer import ReviewCandidate, choose_review_candidate, filter_review_candidates
from app.services.review_scheduler import schedule_next_review
from app.core.time import local_now, to_local_iso

router = APIRouter(prefix="/api/review", tags=["review"])


class ReviewAnswer(BaseModel):
    rating: str


def serialize_review_card(card: ReviewCard, highlight: Highlight, book: Book) -> dict[str, object]:
    return {
        "id": card.id,
        "book_id": book.book_id,
        "book": book.title,
        "author": book.author,
        "chapter": highlight.chapter_title,
        "question": card.question,
        "text": highlight.mark_text,
        "note": "",
        "due": to_local_iso(card.next_review_at),
        "memory_level": card.memory_level,
        "weread_url": highlight.weread_url,
    }


def today_range() -> tuple[datetime, datetime]:
    start = local_now().replace(hour=0, minute=0, second=0, microsecond=0)
    return start, start + timedelta(days=1)


@router.get("/today")
def get_today_review(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[dict[str, object]]:
    now = local_now()
    rows = (
        db.query(ReviewCard, Highlight, Book)
        .join(Highlight, Highlight.id == ReviewCard.highlight_id)
        .join(Book, (Book.user_id == Highlight.user_id) & (Book.book_id == Highlight.book_id))
        .filter(ReviewCard.user_id == current_user.id, ReviewCard.status == "active", ReviewCard.next_review_at <= now)
        .order_by(ReviewCard.next_review_at.asc())
        .limit(50)
        .all()
    )
    return [serialize_review_card(card, highlight, book) for card, highlight, book in rows]


@router.get("/today/stats")
def get_today_review_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    start, end = today_range()
    reviewed_count = (
        db.query(ReviewLog)
        .filter(
            ReviewLog.user_id == current_user.id,
            ReviewLog.created_at >= start,
            ReviewLog.created_at < end,
        )
        .count()
    )
    rows = (
        db.query(ReviewLog, ReviewCard, Highlight, Book)
        .join(ReviewCard, ReviewCard.id == ReviewLog.review_card_id)
        .join(Highlight, Highlight.id == ReviewCard.highlight_id)
        .join(Book, (Book.user_id == Highlight.user_id) & (Book.book_id == Highlight.book_id))
        .filter(
            ReviewLog.user_id == current_user.id,
            ReviewLog.created_at >= start,
            ReviewLog.created_at < end,
        )
        .order_by(ReviewLog.created_at.desc())
        .limit(5)
        .all()
    )
    return {
        "reviewed_count": reviewed_count,
        "reviewed_items": [
            {
                "id": log.id,
                "card_id": card.id,
                "book": book.title,
                "chapter": highlight.chapter_title,
                "text": highlight.mark_text,
                "rating": log.rating,
                "reviewed_at": to_local_iso(log.created_at),
            }
            for log, card, highlight, book in rows
        ],
    }


@router.get("/random")
def get_random_review_card(
    mode: str = Query(default="random"),
    book_id: str | None = Query(default=None),
    category: str | None = Query(default=None),
    exclude_book_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object] | None:
    now = local_now()
    rows = (
        db.query(ReviewCard, Highlight, Book)
        .join(Highlight, Highlight.id == ReviewCard.highlight_id)
        .join(Book, (Book.user_id == Highlight.user_id) & (Book.book_id == Highlight.book_id))
        .filter(
            ReviewCard.user_id == current_user.id,
            ReviewCard.status == "active",
            ReviewCard.next_review_at <= now,
        )
        .all()
    )
    candidates = [ReviewCandidate(card=card, highlight=highlight, book=book) for card, highlight, book in rows]
    candidates = filter_review_candidates(candidates, mode=mode, book_id=book_id, category=category)
    if not candidates:
        return None

    recent_logs = (
        db.query(ReviewLog)
        .filter(ReviewLog.user_id == current_user.id)
        .order_by(ReviewLog.created_at.desc())
        .limit(1000)
        .all()
    )
    selected = choose_review_candidate(candidates, recent_logs=recent_logs, now=now, exclude_book_id=exclude_book_id)
    if selected is None:
        return None
    return serialize_review_card(selected.card, selected.highlight, selected.book)


@router.post("/cards/{card_id}/answer")
def answer_review_card(
    card_id: int,
    answer: ReviewAnswer,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    card = db.query(ReviewCard).filter(ReviewCard.id == card_id, ReviewCard.user_id == current_user.id).first()
    if card is None:
        raise HTTPException(status_code=404, detail="Review card not found")

    now = local_now()
    previous_next_review_at = card.next_review_at
    result = schedule_next_review(answer.rating, now=now, memory_level=card.memory_level)
    card.next_review_at = result.next_review_at
    card.memory_level = result.memory_level
    card.last_reviewed_at = now
    card.review_count += 1
    db.add(
        ReviewLog(
            review_card_id=card.id,
            user_id=current_user.id,
            rating=answer.rating,
            previous_next_review_at=previous_next_review_at,
            next_review_at=result.next_review_at,
        )
    )
    db.commit()
    db.refresh(card)
    return {
        "card_id": card_id,
        "rating": answer.rating,
        "next_review_at": to_local_iso(result.next_review_at),
        "memory_level": result.memory_level,
        "review_count": 1,
    }
