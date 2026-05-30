from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import Book, Collection, CollectionHighlight, Highlight, User
from app.db.session import get_db

router = APIRouter(prefix="/api/collections", tags=["collections"])


class CollectionPayload(BaseModel):
    name: str
    description: str | None = None


class CollectionHighlightPayload(BaseModel):
    highlight_id: int


@router.get("")
def list_collections(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[dict[str, object]]:
    rows = (
        db.query(Collection)
        .filter(Collection.user_id == current_user.id)
        .order_by(Collection.updated_at.desc(), Collection.id.desc())
        .all()
    )
    return [
        {
            "id": collection.id,
            "name": collection.name,
            "description": collection.description,
            "highlight_count": len(collection.highlights),
        }
        for collection in rows
    ]


@router.post("")
def create_collection(
    payload: CollectionPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    collection = Collection(
        user_id=current_user.id,
        name=payload.name.strip(),
        description=(payload.description or "").strip() or None,
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return {"id": collection.id, "name": collection.name, "description": collection.description, "highlight_count": 0}


@router.patch("/{collection_id}")
def update_collection(
    collection_id: int,
    payload: CollectionPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    collection = (
        db.query(Collection)
        .filter(Collection.id == collection_id, Collection.user_id == current_user.id)
        .first()
    )
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    collection.name = payload.name.strip()
    collection.description = (payload.description or "").strip() or None
    db.commit()
    db.refresh(collection)
    return {
        "id": collection.id,
        "name": collection.name,
        "description": collection.description,
        "highlight_count": len(collection.highlights),
    }


@router.delete("/{collection_id}")
def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, bool]:
    collection = (
        db.query(Collection)
        .filter(Collection.id == collection_id, Collection.user_id == current_user.id)
        .first()
    )
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    db.delete(collection)
    db.commit()
    return {"ok": True}


@router.get("/{collection_id}")
def get_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    collection = (
        db.query(Collection)
        .filter(Collection.id == collection_id, Collection.user_id == current_user.id)
        .first()
    )
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")

    rows = (
        db.query(CollectionHighlight, Highlight, Book)
        .join(Highlight, Highlight.id == CollectionHighlight.highlight_id)
        .join(Book, (Book.user_id == Highlight.user_id) & (Book.book_id == Highlight.book_id))
        .filter(CollectionHighlight.collection_id == collection_id, CollectionHighlight.user_id == current_user.id)
        .order_by(CollectionHighlight.created_at.desc())
        .all()
    )
    return {
        "id": collection.id,
        "name": collection.name,
        "description": collection.description,
        "highlights": [
            {
                "id": highlight.id,
                "book": book.title,
                "author": book.author,
                "category": book.category,
                "chapter": highlight.chapter_title,
                "text": highlight.mark_text,
            }
            for _, highlight, book in rows
        ],
    }


@router.post("/{collection_id}/highlights")
def add_collection_highlight(
    collection_id: int,
    payload: CollectionHighlightPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, bool]:
    collection = (
        db.query(Collection)
        .filter(Collection.id == collection_id, Collection.user_id == current_user.id)
        .first()
    )
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")

    highlight = (
        db.query(Highlight)
        .filter(Highlight.id == payload.highlight_id, Highlight.user_id == current_user.id)
        .first()
    )
    if highlight is None:
        raise HTTPException(status_code=404, detail="Highlight not found")

    existing = (
        db.query(CollectionHighlight)
        .filter(
            CollectionHighlight.user_id == current_user.id,
            CollectionHighlight.collection_id == collection_id,
            CollectionHighlight.highlight_id == payload.highlight_id,
        )
        .first()
    )
    if existing is None:
        db.add(
            CollectionHighlight(
                user_id=current_user.id,
                collection_id=collection_id,
                highlight_id=payload.highlight_id,
            )
        )
        db.commit()
    return {"ok": True}


@router.get("/{collection_id}/export/markdown")
def export_collection_markdown(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    detail = get_collection(collection_id, db=db, current_user=current_user)
    lines = [f"# {detail['name']}", ""]
    if detail["description"]:
        lines.extend([str(detail["description"]), ""])
    for item in detail["highlights"]:
        lines.extend(
            [
                f"## {item['book']}",
                f"- 作者：{item['author'] or '未知作者'}",
                f"- 分类：{item['category'] or '未分类'}",
                f"- 章节：{item['chapter'] or '未识别章节'}",
                "",
                item["text"],
                "",
            ]
        )
    return {"markdown": "\n".join(lines).strip()}
