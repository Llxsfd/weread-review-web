from fastapi import APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import Book, Highlight, ReviewCard, ReviewLog, SyncJob, UserNote
from app.db.models import User
from app.db.session import get_db
from fastapi import Depends
from app.core.time import local_now, to_local_iso

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict[str, object]:
    now = local_now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    latest_sync = (
        db.query(SyncJob).filter(SyncJob.user_id == current_user.id).order_by(SyncJob.finished_at.desc()).first()
    )
    book_count = db.query(func.count(Book.id)).filter(Book.user_id == current_user.id).scalar() or 0
    finished_count = (
        db.query(func.count(Book.id))
        .filter(Book.user_id == current_user.id, (Book.reading_progress >= 100) | (Book.marked_status == 1))
        .scalar()
        or 0
    )
    highlight_count = db.query(func.count(Highlight.id)).filter(Highlight.user_id == current_user.id).scalar() or 0
    note_count = db.query(func.count(UserNote.id)).filter(UserNote.user_id == current_user.id).scalar() or 0
    card_count = db.query(func.count(ReviewCard.id)).filter(ReviewCard.user_id == current_user.id).scalar() or 0
    reviewed_card_count = (
        db.query(func.count(ReviewCard.id))
        .filter(ReviewCard.user_id == current_user.id, ReviewCard.review_count > 0)
        .scalar()
        or 0
    )
    mastered_count = (
        db.query(func.count(ReviewCard.id))
        .filter(ReviewCard.user_id == current_user.id, ReviewCard.memory_level >= 5)
        .scalar()
        or 0
    )
    active_count = (
        db.query(func.count(ReviewCard.id))
        .filter(ReviewCard.user_id == current_user.id, ReviewCard.status == "active")
        .scalar()
        or 0
    )
    top_books = (
        db.query(Book.title, Book.author, Book.cover, Book.category, func.count(Highlight.id).label("highlight_count"))
        .join(Highlight, (Highlight.user_id == Book.user_id) & (Highlight.book_id == Book.book_id))
        .filter(Book.user_id == current_user.id)
        .group_by(Book.id)
        .order_by(func.count(Highlight.id).desc())
        .limit(6)
        .all()
    )
    category_rows = (
        db.query(Book.category, func.count(Book.id).label("book_count"))
        .filter(Book.user_id == current_user.id)
        .group_by(Book.category)
        .order_by(func.count(Book.id).desc())
        .limit(5)
        .all()
    )
    return {
        "book_count": book_count,
        "finished_book_count": finished_count,
        "reading_book_count": max(book_count - finished_count, 0),
        "highlight_count": highlight_count,
        "user_note_count": note_count,
        "review_card_count": card_count,
        "due_today_count": db.query(func.count(ReviewCard.id))
        .filter(ReviewCard.user_id == current_user.id, ReviewCard.status == "active", ReviewCard.next_review_at <= now)
        .scalar()
        or 0,
        "overdue_count": db.query(func.count(ReviewCard.id))
        .filter(ReviewCard.user_id == current_user.id, ReviewCard.status == "active", ReviewCard.next_review_at < today_start)
        .scalar()
        or 0,
        "reviewed_today_count": db.query(func.count(ReviewLog.id))
        .filter(ReviewLog.user_id == current_user.id, ReviewLog.created_at >= today_start)
        .scalar()
        or 0,
        "latest_sync_at": to_local_iso(latest_sync.finished_at) if latest_sync else None,
        "note_composition": [
            {"label": "划线", "value": highlight_count},
            {"label": "想法", "value": note_count},
            {"label": "复习卡", "value": card_count},
        ],
        "review_status": [
            {"label": "待复习", "value": active_count},
            {"label": "已复习", "value": reviewed_card_count},
            {"label": "已掌握", "value": mastered_count},
        ],
        "category_distribution": [
            {"label": category or "未分类", "value": int(count or 0)}
            for category, count in category_rows
        ],
        "top_highlight_books": [
            {
                "title": title,
                "author": author,
                "cover": cover,
                "category": category,
                "highlight_count": int(count or 0),
            }
            for title, author, cover, category, count in top_books
        ],
    }
