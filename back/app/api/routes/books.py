from fastapi import APIRouter, Query
from fastapi import Depends
from sqlalchemy import or_
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import Book, Highlight, ReviewCard
from app.db.models import User
from app.db.session import get_db
from app.core.time import to_local_iso

router = APIRouter(prefix="/api/books", tags=["books"])


@router.get("")
def list_books(
    q: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, object]]:
    query = (
        db.query(
            Book,
            func.count(Highlight.id).label("highlight_count"),
            func.count(ReviewCard.id).label("due_count"),
        )
        .outerjoin(Highlight, (Highlight.user_id == Book.user_id) & (Highlight.book_id == Book.book_id))
        .outerjoin(ReviewCard, (ReviewCard.highlight_id == Highlight.id) & (ReviewCard.status == "active"))
        .filter(Book.user_id == current_user.id)
    )
    keyword = (q or "").strip()
    if keyword:
        like_keyword = f"%{keyword}%"
        query = query.filter(or_(Book.title.like(like_keyword), Book.author.like(like_keyword)))

    rows = query.group_by(Book.id).order_by(Book.updated_at.desc()).all()
    return [
        {
            "id": book.book_id,
            "title": book.title,
            "author": book.author,
            "category": book.category,
            "cover": book.cover,
            "progress": book.reading_progress,
            "highlights": int(highlight_count or 0),
            "due": int(due_count or 0),
        }
        for book, highlight_count, due_count in rows
    ]


@router.get("/{book_id}/highlights")
def list_book_highlights(
    book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, object]]:
    rows = (
        db.query(Highlight, ReviewCard)
        .outerjoin(ReviewCard, ReviewCard.highlight_id == Highlight.id)
        .filter(Highlight.user_id == current_user.id, Highlight.book_id == book_id)
        .order_by(Highlight.created_at_weread.desc(), Highlight.id.desc())
        .all()
    )
    return [
        {
            "id": highlight.id,
            "chapter": highlight.chapter_title,
            "text": highlight.mark_text,
            "created_at": to_local_iso(highlight.created_at_weread),
            "next_review": to_local_iso(card.next_review_at) if card else None,
            "status": card.status if card else "未建卡",
            "weread_url": highlight.weread_url,
        }
        for highlight, card in rows
    ]
