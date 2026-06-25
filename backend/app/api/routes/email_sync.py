import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.email_service import get_last_email_sync, run_email_sync

router = APIRouter(prefix="/api/email-sync", tags=["email-sync"])


@router.post("")
def trigger_email_sync(db: Session = Depends(get_db)):
    result = run_email_sync(db)
    return result


@router.get("/status")
def email_sync_status(db: Session = Depends(get_db)):
    job = get_last_email_sync(db)
    if not job:
        return {"status": "never_run"}
    return {
        "id": str(job.id),
        "status": job.status,
        "imported": job.imported,
        "ignored": job.ignored,
        "errors": json.loads(job.errors) if job.errors else [],
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }
