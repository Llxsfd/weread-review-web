from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.time import local_now
from app.db.models import Book, Highlight, ReviewCard, ReviewLog, User
from app.db.session import get_db

router = APIRouter(prefix="/api/data-center", tags=["data-center"])


def chart_item(label: str | None, value: int) -> dict[str, object]:
    return {"label": label or "未分类", "value": int(value or 0)}


def get_summary_payload(db: Session, user_id: int) -> dict[str, Any]:
    book_count = db.query(func.count(Book.id)).filter(Book.user_id == user_id).scalar() or 0
    highlight_count = db.query(func.count(Highlight.id)).filter(Highlight.user_id == user_id).scalar() or 0
    reviewed_highlight_count = (
        db.query(func.count(ReviewCard.id))
        .filter(ReviewCard.user_id == user_id, ReviewCard.review_count > 0)
        .scalar()
        or 0
    )
    avg_highlights = round(int(highlight_count) / int(book_count), 1) if book_count else 0

    return {
        "book_count": int(book_count),
        "highlight_count": int(highlight_count),
        "reviewed_highlight_count": int(reviewed_highlight_count),
        "avg_highlights_per_book": avg_highlights,
    }


def get_distribution_payload(db: Session, user_id: int) -> dict[str, Any]:
    category_rows = (
        db.query(Book.category, func.count(Book.id))
        .filter(Book.user_id == user_id)
        .group_by(Book.category)
        .order_by(func.count(Book.id).desc())
        .limit(10)
        .all()
    )
    author_rows = (
        db.query(Book.author, func.count(Book.id))
        .filter(Book.user_id == user_id)
        .group_by(Book.author)
        .order_by(func.count(Book.id).desc())
        .limit(10)
        .all()
    )

    progress_rows = (
        db.query(
            case(
                (Book.reading_progress >= 100, "已读完"),
                (Book.marked_status.in_([1, 4]), "已读完"),
                (Book.reading_progress <= 25, "0-25%"),
                (Book.reading_progress <= 50, "26-50%"),
                (Book.reading_progress <= 75, "51-75%"),
                else_="76-99%",
            ).label("bucket"),
            func.count(Book.id),
        )
        .filter(Book.user_id == user_id)
        .group_by("bucket")
        .all()
    )
    progress_map = {label: int(count or 0) for label, count in progress_rows}
    reading_progress = [
        {"label": "0-25%", "value": progress_map.get("0-25%", 0)},
        {"label": "26-50%", "value": progress_map.get("26-50%", 0)},
        {"label": "51-75%", "value": progress_map.get("51-75%", 0)},
        {"label": "76-99%", "value": progress_map.get("76-99%", 0)},
        {"label": "已读完", "value": progress_map.get("已读完", 0)},
    ]

    memory_rows = (
        db.query(
            case(
                (ReviewCard.memory_level <= 3, "模糊"),
                (ReviewCard.memory_level == 4, "记得"),
                else_="熟悉",
            ).label("bucket"),
            func.count(ReviewCard.id),
        )
        .filter(ReviewCard.user_id == user_id, ReviewCard.review_count > 0)
        .group_by("bucket")
        .all()
    )
    memory_map = {label: int(count or 0) for label, count in memory_rows}
    memory_distribution = [
        {"label": "模糊", "value": memory_map.get("模糊", 0)},
        {"label": "记得", "value": memory_map.get("记得", 0)},
        {"label": "熟悉", "value": memory_map.get("熟悉", 0)},
    ]

    return {
        "category_distribution": [chart_item(category, count) for category, count in category_rows],
        "author_distribution": [chart_item(author or "未知作者", count) for author, count in author_rows],
        "reading_progress": reading_progress,
        "memory_distribution": memory_distribution,
    }


def get_review_payload(db: Session, user_id: int) -> dict[str, Any]:
    summary = get_summary_payload(db, user_id)
    mastered_highlight_count = (
        db.query(func.count(ReviewCard.id))
        .filter(ReviewCard.user_id == user_id, ReviewCard.review_count > 0, ReviewCard.memory_level >= 5)
        .scalar()
        or 0
    )

    today = local_now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_day = today - timedelta(days=13)
    trend_rows = (
        db.query(func.date(ReviewLog.created_at), func.count(ReviewLog.id))
        .filter(ReviewLog.user_id == user_id, ReviewLog.created_at >= start_day)
        .group_by(func.date(ReviewLog.created_at))
        .all()
    )
    trend_map = {str(day): int(count or 0) for day, count in trend_rows}
    review_trend = []
    for offset in range(13, -1, -1):
        day = today - timedelta(days=offset)
        review_trend.append({"label": day.strftime("%m-%d"), "value": trend_map.get(day.date().isoformat(), 0)})

    category_card_rows = (
        db.query(
            Book.category,
            func.count(ReviewCard.id).label("highlights"),
            func.sum(case((ReviewCard.review_count > 0, 1), else_=0)).label("reviewed"),
            func.sum(case(((ReviewCard.review_count > 0) & (ReviewCard.memory_level >= 5), 1), else_=0)).label("mastered"),
        )
        .join(Highlight, (Highlight.user_id == Book.user_id) & (Highlight.book_id == Book.book_id))
        .join(ReviewCard, (ReviewCard.user_id == Highlight.user_id) & (ReviewCard.highlight_id == Highlight.id))
        .filter(Book.user_id == user_id)
        .group_by(Book.category)
        .all()
    )
    category_rows: dict[str, dict[str, int | str]] = {}
    for category, highlights, reviewed, mastered in category_card_rows:
        label = category or "未分类"
        category_rows[label] = {
            "label": label,
            "highlights": int(highlights or 0),
            "reviewed": int(reviewed or 0),
            "mastered": int(mastered or 0),
            "forgot_or_hard": 0,
        }

    hard_rows = (
        db.query(Book.category, func.count(ReviewLog.id))
        .join(Highlight, (Highlight.user_id == Book.user_id) & (Highlight.book_id == Book.book_id))
        .join(ReviewCard, (ReviewCard.user_id == Highlight.user_id) & (ReviewCard.highlight_id == Highlight.id))
        .join(ReviewLog, (ReviewLog.user_id == ReviewCard.user_id) & (ReviewLog.review_card_id == ReviewCard.id))
        .filter(Book.user_id == user_id, ReviewLog.rating.in_(["forgot", "hard"]))
        .group_by(Book.category)
        .all()
    )
    for category, count in hard_rows:
        label = category or "未分类"
        row = category_rows.setdefault(
            label,
            {"label": label, "highlights": 0, "reviewed": 0, "mastered": 0, "forgot_or_hard": 0},
        )
        row["forgot_or_hard"] = int(count or 0)

    stale_30_threshold = today - timedelta(days=30)
    stale_90_threshold = today - timedelta(days=90)
    stale_highlights = [
        {
            "label": "30 天未复习",
            "value": int(
                db.query(func.count(ReviewCard.id))
                .filter(
                    ReviewCard.user_id == user_id,
                    ReviewCard.review_count > 0,
                    ReviewCard.last_reviewed_at <= stale_30_threshold,
                )
                .scalar()
                or 0
            ),
        },
        {
            "label": "90 天未复习",
            "value": int(
                db.query(func.count(ReviewCard.id))
                .filter(
                    ReviewCard.user_id == user_id,
                    ReviewCard.review_count > 0,
                    ReviewCard.last_reviewed_at <= stale_90_threshold,
                )
                .scalar()
                or 0
            ),
        },
        {
            "label": "从未复习",
            "value": int(
                db.query(func.count(ReviewCard.id))
                .filter(ReviewCard.user_id == user_id, ReviewCard.review_count <= 0)
                .scalar()
                or 0
            ),
        },
    ]

    return {
        "review_funnel": [
            {"label": "书籍", "value": summary["book_count"]},
            {"label": "划线", "value": summary["highlight_count"]},
            {"label": "已复习划线", "value": summary["reviewed_highlight_count"]},
            {"label": "熟悉划线", "value": int(mastered_highlight_count)},
        ],
        "category_review_effect": sorted(
            category_rows.values(),
            key=lambda item: (int(item["reviewed"]), int(item["highlights"])),
            reverse=True,
        ),
        "review_trend": review_trend,
        "stale_highlights": stale_highlights,
    }


def get_books_payload(db: Session, user_id: int) -> dict[str, Any]:
    top_highlight_rows = (
        db.query(Book.title, Book.author, Book.category, Book.cover, func.count(Highlight.id).label("highlight_count"))
        .join(Highlight, (Highlight.user_id == Book.user_id) & (Highlight.book_id == Book.book_id))
        .filter(Book.user_id == user_id)
        .group_by(Book.id)
        .order_by(func.count(Highlight.id).desc())
        .limit(8)
        .all()
    )
    return {
        "top_highlight_books": [
            {
                "title": title,
                "author": author,
                "category": category,
                "cover": cover,
                "highlight_count": int(count or 0),
            }
            for title, author, category, cover, count in top_highlight_rows
        ]
    }


@router.get("")
def get_data_center(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    summary = get_summary_payload(db, current_user.id)
    distributions = get_distribution_payload(db, current_user.id)
    review = get_review_payload(db, current_user.id)
    books = get_books_payload(db, current_user.id)
    return {"summary": summary, **distributions, **review, **books}


@router.get("/summary")
def get_data_center_summary(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    return get_summary_payload(db, current_user.id)


@router.get("/distributions")
def get_data_center_distributions(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    return get_distribution_payload(db, current_user.id)


@router.get("/review")
def get_data_center_review(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    return get_review_payload(db, current_user.id)


@router.get("/books")
def get_data_center_books(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    return get_books_payload(db, current_user.id)
