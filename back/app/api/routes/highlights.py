from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_current_user
from app.db.models import Book, Highlight, ReviewCard
from app.db.models import User
from app.db.session import get_db
from app.core.time import to_local_iso

router = APIRouter(prefix="/api/highlights", tags=["highlights"])


@router.get("")
def list_highlights(
    q: str | None = Query(default=None),
    book: str | None = Query(default=None),
    author: str | None = Query(default=None),
    category: str | None = Query(default=None),
    chapter: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    query = (
        db.query(Highlight, Book, ReviewCard)
        .join(Book, (Book.user_id == Highlight.user_id) & (Book.book_id == Highlight.book_id))
        .outerjoin(ReviewCard, ReviewCard.highlight_id == Highlight.id)
        .filter(Highlight.user_id == current_user.id)
    )
    if q:
        keyword = f"%{q.strip()}%"
        query = query.filter(
            (Book.title.like(keyword))
            | (Book.author.like(keyword))
            | (Book.category.like(keyword))
            | (Highlight.chapter_title.like(keyword))
            | (Highlight.mark_text.like(keyword))
        )
    if book:
        query = query.filter(Book.title.like(f"%{book.strip()}%"))
    if author:
        query = query.filter(Book.author.like(f"%{author.strip()}%"))
    if category:
        query = query.filter(Book.category.like(f"%{category.strip()}%"))
    if chapter:
        query = query.filter(Highlight.chapter_title.like(f"%{chapter.strip()}%"))

    total = query.with_entities(func.count(Highlight.id)).scalar() or 0
    rows = (
        query.order_by(Highlight.created_at_weread.desc(), Highlight.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [
            {
                "id": highlight.id,
                "book": book.title,
                "author": book.author,
                "category": book.category,
                "chapter": highlight.chapter_title,
                "text": highlight.mark_text,
                "next_review": to_local_iso(card.next_review_at) if card else None,
                "status": card.status if card else "未建卡",
                "weread_url": highlight.weread_url,
            }
            for highlight, book, card in rows
        ],
        "total": int(total),
        "page": page,
        "page_size": page_size,
    }
