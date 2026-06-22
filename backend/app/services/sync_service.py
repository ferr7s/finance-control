from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.sync_job import SyncJob

BANKS = ["flash", "itau", "nubank"]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_sync_job(db: Session, bank: str) -> SyncJob:
    job = SyncJob(bank=bank, status="pending", started_at=_now())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def complete_sync_job(db: Session, job: SyncJob, synced: int, error: str | None = None) -> SyncJob:
    job.status = "failed" if error else "done"
    job.transactions_synced = synced
    job.error = error
    job.completed_at = _now()
    db.commit()
    db.refresh(job)
    return job


def get_last_sync_status(db: Session) -> list[dict]:
    results = []
    for bank in BANKS:
        job = db.scalar(
            select(SyncJob)
            .where(SyncJob.bank == bank)
            .order_by(SyncJob.started_at.desc())
            .limit(1)
        )
        results.append({
            "bank": bank,
            "status": job.status if job else "idle",
            "transactions_synced": job.transactions_synced if job else 0,
            "error": job.error if job else None,
            "synced_at": job.completed_at.isoformat() if job and job.completed_at else None,
        })
    return results


async def trigger_sync(db: Session, bank: str | None = None) -> list[SyncJob]:
    settings = get_settings()
    banks = [bank] if bank else BANKS
    jobs = []

    for b in banks:
        job = create_sync_job(db, b)
        jobs.append(job)
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                await client.post(f"{settings.sync_server_url}/sync/{b}")
        except Exception as e:
            complete_sync_job(db, job, synced=0, error=f"Sync server unreachable: {e}")

    return jobs
