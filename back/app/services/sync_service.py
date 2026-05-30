import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Protocol

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.time import from_unix_timestamp, local_now
from app.db.models import Book, Chapter, Highlight, ReviewCard, Setting, SyncJob, UserNote
from app.db.session import SessionLocal
from app.services.weread_client import WeReadClient, WeReadError


class WeReadClientLike(Protocol):
    async def fetch_notebooks(self, *, count: int = 100, last_sort: int | None = None) -> dict[str, Any]:
        ...

    async def fetch_book_info(self, book_id: str) -> dict[str, Any]:
        ...

    async def fetch_book_highlights(self, book_id: str) -> dict[str, Any]:
        ...

    async def fetch_my_reviews(self, book_id: str, *, count: int = 100, synckey: int = 0) -> dict[str, Any]:
        ...


class SyncCancelled(RuntimeError):
    pass


@dataclass(frozen=True)
class SyncResult:
    job_id: int | None
    status: str
    books_synced: int
    highlights_synced: int
    message: str


class SyncService:
    def __init__(
        self,
        *,
        db: Session,
        user_id: int | None = None,
        weread_client_factory: Callable[[str], WeReadClientLike] | None = None,
        now: Callable[[], datetime] = local_now,
    ) -> None:
        self.db = db
        self.user_id = user_id
        self.now = now
        settings = get_settings()
        self.weread_client_factory = weread_client_factory or (
            lambda api_key: WeReadClient(
                api_key=api_key,
                skill_version=settings.weread_skill_version,
                base_url=settings.weread_api_base,
            )
        )

    def run_full_sync(self) -> SyncResult:
        return asyncio.run(self.run_full_sync_async())

    def run_quick_sync(self) -> SyncResult:
        return asyncio.run(self.run_full_sync_async(mode="quick"))

    def create_full_sync_job(self, *, mode: str = "full") -> SyncResult:
        job = SyncJob(
            user_id=self.user_id,
            job_type=mode,
            status="running",
            message=self._format_log([f"准备开始{sync_mode_label(mode)}微信读书数据"]),
            started_at=self.now(),
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return SyncResult(job.id, job.status, 0, 0, job.message or "")

    @classmethod
    def run_existing_job(cls, *, job_id: int, user_id: int, mode: str = "full") -> None:
        db = SessionLocal()
        try:
            service = cls(db=db, user_id=user_id)
            asyncio.run(service.run_existing_job_async(job_id, mode=mode))
        finally:
            db.close()

    async def run_existing_job_async(self, job_id: int, *, mode: str = "full") -> None:
        job = self.db.query(SyncJob).filter(SyncJob.id == job_id, SyncJob.user_id == self.user_id).first()
        if job is None:
            return
        if job.status == "cancel_requested":
            job.status = "cancelled"
            job.finished_at = self.now()
            self.db.commit()
            return

        logs = self._parse_log(job.message)
        try:
            self._append_log(job, logs, "读取当前用户保存的 WeRead API Key")
            api_key = self._get_weread_api_key()
            client = self.weread_client_factory(api_key)

            self._append_log(job, logs, f"请求笔记本概览：/user/notebooks（{sync_mode_label(mode)}）")
            notebooks = await self._fetch_all_notebooks(client, job=job, logs=logs)
            self._append_log(job, logs, f"笔记本概览完成：共 {len(notebooks)} 本有笔记的书")

            for index, item in enumerate(notebooks, start=1):
                self._raise_if_cancelled(job, logs)
                title = (item.get("book") or {}).get("title") or item.get("bookId") or "未命名书籍"
                if mode == "quick" and self._is_notebook_item_unchanged(item):
                    self._append_log(job, logs, f"[{index}/{len(notebooks)}] 跳过《{title}》：本地已是最新")
                    job.books_synced = index
                    self.db.commit()
                    continue
                self._append_log(job, logs, f"[{index}/{len(notebooks)}] 同步《{title}》基础信息")
                book = self._upsert_book(item)
                self._append_log(job, logs, f"[{index}/{len(notebooks)}] 请求《{book.title}》书籍详情：/book/info")
                self._raise_if_cancelled(job, logs)
                book_info = await client.fetch_book_info(book.book_id)
                self._raise_if_cancelled(job, logs)
                book = self._upsert_book(item, detail=book_info)
                job.books_synced += 1
                job.books_synced = index
                self.db.commit()

                self._append_log(job, logs, f"[{index}/{len(notebooks)}] 请求《{book.title}》划线：/book/bookmarklist")
                self._raise_if_cancelled(job, logs)
                added = await self._sync_book_highlights(client, book.book_id, job=job, logs=logs)
                self._raise_if_cancelled(job, logs)
                job.highlights_synced += added
                self.db.commit()
                self._append_log(job, logs, f"[{index}/{len(notebooks)}] 《{book.title}》划线入库 {added} 条")

                self._append_log(job, logs, f"[{index}/{len(notebooks)}] 请求《{book.title}》个人想法：/review/list/mine")
                self._raise_if_cancelled(job, logs)
                await self._sync_book_reviews(client, book.book_id, job=job, logs=logs)
                self._append_log(job, logs, f"[{index}/{len(notebooks)}] 《{book.title}》个人想法同步完成")

            job.status = "success"
            job.finished_at = self.now()
            self._append_log(job, logs, f"同步完成：{job.books_synced} 本书，{job.highlights_synced} 条划线")
        except SyncCancelled:
            job.status = "cancelled"
            job.finished_at = self.now()
            self._append_log(job, logs, "同步已中止")
        except Exception as exc:
            if job.status == "cancel_requested":
                job.status = "cancelled"
                job.finished_at = self.now()
                self._append_log(job, logs, "同步已中止")
            else:
                job.status = "failed"
                job.finished_at = self.now()
                self._append_log(job, logs, f"同步失败：{exc}")
        finally:
            self.db.commit()

    def _raise_if_cancelled(self, job: SyncJob, logs: list[str]) -> None:
        self.db.refresh(job)
        if job.status == "cancel_requested":
            self._append_log(job, logs, "收到中止请求，正在停止任务")
            raise SyncCancelled()

    async def run_full_sync_async(self, *, mode: str = "full") -> SyncResult:
        job = SyncJob(user_id=self.user_id, job_type=mode, status="running", started_at=self.now())
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        try:
            api_key = self._get_weread_api_key()
            client = self.weread_client_factory(api_key)
            notebooks = await self._fetch_all_notebooks(client)

            books_synced = 0
            highlights_synced = 0
            for item in notebooks:
                if mode == "quick" and self._is_notebook_item_unchanged(item):
                    continue
                book = self._upsert_book(item)
                book_info = await client.fetch_book_info(book.book_id)
                book = self._upsert_book(item, detail=book_info)
                books_synced += 1
                highlights_synced += await self._sync_book_highlights(client, book.book_id)
                await self._sync_book_reviews(client, book.book_id)

            job.status = "success"
            job.message = "Sync completed"
            job.books_synced = books_synced
            job.highlights_synced = highlights_synced
            job.finished_at = self.now()
            self.db.commit()
            return SyncResult(job.id, job.status, books_synced, highlights_synced, job.message or "")
        except Exception as exc:
            job.status = "failed"
            job.message = str(exc)
            job.finished_at = self.now()
            self.db.commit()
            return SyncResult(job.id, "failed", job.books_synced, job.highlights_synced, job.message or "")

    def _get_weread_api_key(self) -> str:
        setting = (
            self.db.query(Setting)
            .filter(Setting.user_id == self.user_id, Setting.key == "weread_api_key")
            .first()
        )
        if setting is None or not setting.value.strip():
            raise ValueError("WeRead API Key is not configured")
        return setting.value.strip()

    async def _fetch_all_notebooks(
        self,
        client: WeReadClientLike,
        job: SyncJob | None = None,
        logs: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        last_sort: int | None = None
        page = 1
        while True:
            if job is not None and logs is not None:
                self._raise_if_cancelled(job, logs)
            if job is not None and logs is not None:
                self._append_log(job, logs, f"拉取笔记本第 {page} 页")
            payload = await client.fetch_notebooks(count=100, last_sort=last_sort)
            if job is not None and logs is not None:
                self._raise_if_cancelled(job, logs)
            books = payload.get("books") or []
            rows.extend(books)
            if not payload.get("hasMore") or not books:
                return rows
            last_sort = books[-1].get("sort")
            page += 1

    def _upsert_book(self, item: dict[str, Any], *, detail: dict[str, Any] | None = None) -> Book:
        book_id = str(item.get("bookId") or item.get("book", {}).get("bookId"))
        if not book_id:
            raise WeReadError("Notebook item missing bookId")

        book_info = item.get("book") or {}
        detail_info = detail or {}
        book = self.db.query(Book).filter(Book.user_id == self.user_id, Book.book_id == book_id).first()
        if book is None:
            book = Book(
                user_id=self.user_id,
                book_id=book_id,
                title=detail_info.get("title") or book_info.get("title") or "未命名书籍",
            )
            self.db.add(book)

        book.title = detail_info.get("title") or book_info.get("title") or book.title
        book.author = detail_info.get("author") or book_info.get("author")
        book.cover = detail_info.get("cover") or book_info.get("cover")
        book.category = detail_info.get("category") or book_info.get("category") or book.category
        book.reading_progress = int(item.get("readingProgress") or 0)
        book.marked_status = int(item.get("markedStatus") or 0)
        book.note_count = int(item.get("noteCount") or 0)
        book.review_count = int(item.get("reviewCount") or 0)
        book.bookmark_count = int(item.get("bookmarkCount") or 0)
        book.last_note_sort = item.get("sort")
        book.last_synced_at = self.now()
        self.db.commit()
        self.db.refresh(book)
        return book

    def _is_notebook_item_unchanged(self, item: dict[str, Any]) -> bool:
        book_id = str(item.get("bookId") or item.get("book", {}).get("bookId"))
        sort = item.get("sort")
        if not book_id or sort is None:
            return False
        existing = self.db.query(Book).filter(Book.user_id == self.user_id, Book.book_id == book_id).first()
        return existing is not None and existing.last_note_sort == sort

    async def _sync_book_highlights(
        self,
        client: WeReadClientLike,
        book_id: str,
        *,
        job: SyncJob | None = None,
        logs: list[str] | None = None,
    ) -> int:
        if job is not None and logs is not None:
            self._raise_if_cancelled(job, logs)
        payload = await client.fetch_book_highlights(book_id)
        if job is not None and logs is not None:
            self._raise_if_cancelled(job, logs)
        chapter_titles = self._upsert_chapters(book_id, payload.get("chapters") or [])
        count = 0
        for index, item in enumerate(payload.get("updated") or [], start=1):
            if job is not None and logs is not None and index % 20 == 1:
                self._raise_if_cancelled(job, logs)
            if int(item.get("type") or 1) != 1:
                continue
            bookmark_id = str(item.get("bookmarkId") or "")
            if not bookmark_id:
                continue

            highlight = (
                self.db.query(Highlight)
                .filter(Highlight.user_id == self.user_id, Highlight.bookmark_id == bookmark_id)
                .first()
            )
            if highlight is None:
                highlight = Highlight(user_id=self.user_id, bookmark_id=bookmark_id, book_id=book_id, mark_text="")
                self.db.add(highlight)
                is_new = True
            else:
                is_new = False

            chapter_uid = item.get("chapterUid")
            highlight.book_id = str(item.get("bookId") or book_id)
            highlight.chapter_uid = chapter_uid
            highlight.chapter_title = chapter_titles.get(chapter_uid)
            highlight.mark_text = item.get("markText") or ""
            highlight.highlight_range = item.get("range")
            highlight.color_style = item.get("colorStyle")
            highlight.created_at_weread = from_unix_timestamp(item.get("createTime"))
            highlight.weread_url = build_weread_highlight_url(
                book_id=highlight.book_id,
                chapter_uid=highlight.chapter_uid,
                highlight_range=highlight.highlight_range,
            )
            self.db.flush()
            self._ensure_review_card(highlight, is_new=is_new)
            count += 1

        self.db.commit()
        return count

    def _upsert_chapters(self, book_id: str, chapters: list[dict[str, Any]]) -> dict[int, str]:
        result: dict[int, str] = {}
        for item in chapters:
            chapter_uid = item.get("chapterUid")
            if chapter_uid is None:
                continue
            result[chapter_uid] = item.get("title") or ""
            chapter = (
                self.db.query(Chapter)
                .filter(Chapter.user_id == self.user_id, Chapter.book_id == book_id, Chapter.chapter_uid == chapter_uid)
                .first()
            )
            if chapter is None:
                chapter = Chapter(user_id=self.user_id, book_id=book_id, chapter_uid=chapter_uid)
                self.db.add(chapter)
            chapter.chapter_idx = item.get("chapterIdx")
            chapter.title = item.get("title")
        self.db.flush()
        return result

    def _ensure_review_card(self, highlight: Highlight, *, is_new: bool) -> None:
        card = (
            self.db.query(ReviewCard)
            .filter(ReviewCard.user_id == self.user_id, ReviewCard.highlight_id == highlight.id)
            .first()
        )
        if card is not None:
            return

        base_time = highlight.created_at_weread or self.now()
        self.db.add(
            ReviewCard(
                highlight_id=highlight.id,
                user_id=self.user_id,
                question="你划过的重点，不该被遗忘在书里",
                memory_level=0,
                difficulty=0,
                review_count=0,
                next_review_at=base_time + timedelta(days=1) if is_new else self.now(),
                status="active",
            )
        )

    async def _sync_book_reviews(
        self,
        client: WeReadClientLike,
        book_id: str,
        *,
        job: SyncJob | None = None,
        logs: list[str] | None = None,
    ) -> None:
        synckey = 0
        while True:
            if job is not None and logs is not None:
                self._raise_if_cancelled(job, logs)
            payload = await client.fetch_my_reviews(book_id, count=100, synckey=synckey)
            if job is not None and logs is not None:
                self._raise_if_cancelled(job, logs)
            for index, item in enumerate(payload.get("reviews") or [], start=1):
                if job is not None and logs is not None and index % 20 == 1:
                    self._raise_if_cancelled(job, logs)
                review = item.get("review") or {}
                review_id = str(review.get("reviewId") or "")
                if not review_id:
                    continue
                note = (
                    self.db.query(UserNote)
                    .filter(UserNote.user_id == self.user_id, UserNote.review_id == review_id)
                    .first()
                )
                if note is None:
                    note = UserNote(user_id=self.user_id, book_id=book_id, review_id=review_id, content="")
                    self.db.add(note)
                note.content = review.get("content") or ""
                note.chapter_name = review.get("chapterName")
                note.star = review.get("star")
                note.created_at_weread = from_unix_timestamp(review.get("createTime"))

            self.db.flush()
            if not payload.get("hasMore"):
                self.db.commit()
                return
            synckey = int(payload.get("synckey") or 0)


def build_weread_highlight_url(
    *,
    book_id: str,
    chapter_uid: int | None,
    highlight_range: str | None,
) -> str | None:
    if not book_id or chapter_uid is None or not highlight_range or "-" not in highlight_range:
        return None
    range_start, range_end = highlight_range.split("-", 1)
    return (
        "weread://bestbookmark?"
        f"bookId={book_id}&chapterUid={chapter_uid}&rangeStart={range_start}&rangeEnd={range_end}"
    )


def _timestamp() -> str:
    return local_now().strftime("%H:%M:%S")


def _line(text: str) -> str:
    return f"[{_timestamp()}] {text}"


def _keep_recent(logs: list[str], limit: int = 300) -> list[str]:
    return logs[-limit:]


def _join_logs(logs: list[str]) -> str:
    return "\n".join(_keep_recent(logs))


def _split_logs(value: str | None) -> list[str]:
    return [line for line in (value or "").splitlines() if line.strip()]


SyncService._parse_log = staticmethod(_split_logs)  # type: ignore[attr-defined]
SyncService._format_log = staticmethod(_join_logs)  # type: ignore[attr-defined]


def _append_log(self: SyncService, job: SyncJob, logs: list[str], text: str) -> None:
    logs.append(_line(text))
    job.message = _join_logs(logs)
    self.db.commit()


SyncService._append_log = _append_log  # type: ignore[attr-defined]


def sync_mode_label(mode: str) -> str:
    return "快速同步" if mode == "quick" else "完整同步"
