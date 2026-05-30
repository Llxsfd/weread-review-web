from threading import Thread
import re

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import SyncJob
from app.db.models import User
from app.db.session import get_db
from app.services.sync_service import SyncService
from app.core.time import local_now, to_local_iso

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.post("/full")
def run_full_sync(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict[str, object]:
    return create_sync_job_response(db=db, current_user=current_user, mode="full")


@router.post("/quick")
def run_quick_sync(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict[str, object]:
    return create_sync_job_response(db=db, current_user=current_user, mode="quick")


def create_sync_job_response(*, db: Session, current_user: User, mode: str) -> dict[str, object]:
    result = SyncService(db=db, user_id=current_user.id).create_full_sync_job(mode=mode)
    Thread(
        target=SyncService.run_existing_job,
        kwargs={"job_id": result.job_id, "user_id": current_user.id, "mode": mode},
        daemon=True,
    ).start()
    return {
        "job_id": result.job_id,
        "status": result.status,
        "books_synced": result.books_synced,
        "highlights_synced": result.highlights_synced,
        "message": result.message,
    }


@router.get("/jobs/{job_id}")
def get_sync_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    job = db.query(SyncJob).filter(SyncJob.id == job_id, SyncJob.user_id == current_user.id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Sync job not found")
    finalize_stale_job(db, job)
    return serialize_job(job)


@router.post("/jobs/{job_id}/cancel")
def cancel_sync_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    job = db.query(SyncJob).filter(SyncJob.id == job_id, SyncJob.user_id == current_user.id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Sync job not found")
    if job.status == "running":
        job.status = "cancel_requested"
        job.message = "\n".join([line for line in [job.message, "收到中止请求，等待当前步骤结束"] if line])
        db.commit()
        db.refresh(job)
    return serialize_job(job)


@router.get("/jobs")
def list_sync_jobs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[dict[str, object]]:
    jobs = (
        db.query(SyncJob)
        .filter(SyncJob.user_id == current_user.id)
        .order_by(SyncJob.started_at.desc())
        .limit(30)
        .all()
    )
    for job in jobs:
        finalize_stale_job(db, job)
    return [
        serialize_job(job)
        for job in jobs
    ]


def serialize_job(job: SyncJob) -> dict[str, object]:
    logs = [line for line in (job.message or "").splitlines() if line.strip()]
    total_books = infer_total_books(logs)
    progress = 0
    if job.status in ("success", "cancelled", "failed") and total_books and job.status == "success":
        progress = 100
    elif total_books:
        progress = min(99, round((job.books_synced / total_books) * 100))
    elif job.status in ("running", "cancel_requested"):
        progress = 5
    return {
        "id": job.id,
        "job_type": job.job_type,
        "status": job.status,
        "books_synced": job.books_synced,
        "highlights_synced": job.highlights_synced,
        "total_books": total_books,
        "progress": progress,
        "message": job.message,
        "logs": logs,
        "started_at": to_local_iso(job.started_at),
        "finished_at": to_local_iso(job.finished_at),
    }


def infer_total_books(logs: list[str]) -> int | None:
    for line in logs:
        match = re.search(r"共\s+(\d+)\s+本有笔记的书", line)
        if match:
            return int(match.group(1))
    for line in reversed(logs):
        match = re.search(r"\[(\d+)/(\d+)\]", line)
        if match:
            return int(match.group(2))
    return None


def finalize_stale_job(db: Session, job: SyncJob) -> None:
    if job.status == "cancel_requested":
        job.status = "cancelled"
        job.finished_at = job.finished_at or local_now()
        job.message = "\n".join([line for line in [job.message, "同步已中止"] if line])
        db.commit()
        db.refresh(job)
    elif job.status == "running" and job.finished_at is None:
        age_seconds = (local_now() - job.started_at).total_seconds()
        if age_seconds > 60 * 60 * 3:
            job.status = "failed"
            job.finished_at = local_now()
            job.message = "\n".join([line for line in [job.message, "任务异常结束，请重新发起同步"] if line])
            db.commit()
            db.refresh(job)
