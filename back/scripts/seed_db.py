from datetime import datetime, timedelta, timezone

from app.core.security import hash_password
from app.db.models import Book, Highlight, ReviewCard, SyncJob, User
from app.db.session import SessionLocal


def main() -> None:
    db = SessionLocal()
    now = datetime.now(timezone.utc)
    try:
        if db.query(User).filter(User.email == "demo@example.com").first():
            print("Seed skipped: books table already has data.")
            return

        user = User(email="demo@example.com", nickname="演示用户", password_hash=hash_password("demo123456"))
        db.add(user)
        db.flush()

        books = [
            Book(user_id=user.id, book_id="demo-1", title="置身事内", author="兰小欢", reading_progress=100, note_count=2, review_count=1),
            Book(user_id=user.id, book_id="demo-2", title="卡片笔记写作法", author="申克·阿伦斯", reading_progress=78, note_count=1, review_count=0),
            Book(user_id=user.id, book_id="demo-3", title="纳瓦尔宝典", author="埃里克·乔根森", reading_progress=100, note_count=1, review_count=0),
        ]
        db.add_all(books)
        db.flush()

        highlights = [
            Highlight(
                book_id="demo-1",
                user_id=user.id,
                bookmark_id="demo-h-1",
                chapter_uid=101,
                chapter_title="地方政府的权力与事务",
                mark_text="地方政府既是政策执行者，也是地方经济发展的组织者，承担着大量具体而复杂的事务。",
                highlight_range="100-180",
                created_at_weread=now - timedelta(days=10),
                weread_url="weread://bestbookmark?bookId=demo-1&chapterUid=101&rangeStart=100&rangeEnd=180",
            ),
            Highlight(
                book_id="demo-2",
                user_id=user.id,
                bookmark_id="demo-h-2",
                chapter_uid=201,
                chapter_title="写作不是线性过程",
                mark_text="写作不是把想法记录下来，而是在记录和连接的过程中产生新的想法。",
                highlight_range="200-288",
                created_at_weread=now - timedelta(days=5),
                weread_url="weread://bestbookmark?bookId=demo-2&chapterUid=201&rangeStart=200&rangeEnd=288",
            ),
            Highlight(
                book_id="demo-3",
                user_id=user.id,
                bookmark_id="demo-h-3",
                chapter_uid=301,
                chapter_title="积累专长",
                mark_text="专长无法被训练出来，否则人人都能掌握。专长往往来自真正的好奇心和长期积累。",
                highlight_range="300-390",
                created_at_weread=now - timedelta(days=20),
                weread_url="weread://bestbookmark?bookId=demo-3&chapterUid=301&rangeStart=300&rangeEnd=390",
            ),
        ]
        db.add_all(highlights)
        db.flush()

        cards = [
            ReviewCard(
                highlight_id=highlights[0].id,
                user_id=user.id,
                question="这条划线如何解释地方政府推动增长的动力？",
                memory_level=2,
                next_review_at=now - timedelta(hours=1),
            ),
            ReviewCard(
                highlight_id=highlights[1].id,
                user_id=user.id,
                question="这条划线提醒我们如何重新理解写作？",
                memory_level=3,
                next_review_at=now + timedelta(days=7),
            ),
            ReviewCard(
                highlight_id=highlights[2].id,
                user_id=user.id,
                question="为什么专长通常无法通过学校直接获得？",
                memory_level=1,
                next_review_at=now - timedelta(days=2),
            ),
        ]
        db.add_all(cards)
        db.add(
            SyncJob(
                job_type="seed",
                user_id=user.id,
                status="success",
                message="Demo data inserted",
                books_synced=len(books),
                highlights_synced=len(highlights),
                started_at=now,
                finished_at=now,
            )
        )
        db.commit()
        print("Demo data inserted.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
