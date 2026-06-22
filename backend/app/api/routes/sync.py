from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.sync_service import get_last_sync_status, trigger_sync

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.post("")
async def sync_all(db: Session = Depends(get_db)):
    jobs = await trigger_sync(db)
    return [{"id": str(j.id), "bank": j.bank, "status": j.status} for j in jobs]


@router.post("/{bank}")
async def sync_bank(bank: str, db: Session = Depends(get_db)):
    jobs = await trigger_sync(db, bank=bank)
    return [{"id": str(j.id), "bank": j.bank, "status": j.status} for j in jobs]


@router.get("/status")
def sync_status(db: Session = Depends(get_db)):
    return get_last_sync_status(db)
