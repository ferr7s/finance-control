from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.import_service import import_bank_csv

router = APIRouter(prefix="/api/import", tags=["import"])


@router.post("/bank-csv")
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    return import_bank_csv(db, content)
