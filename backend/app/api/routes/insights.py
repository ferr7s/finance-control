from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.insight import InsightRead
from app.services import insights_service

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("", response_model=list[InsightRead])
def list_insights(db: Session = Depends(get_db)):
    return insights_service.list_insights(db)


@router.post("/generate", response_model=list[InsightRead])
def generate_insights(db: Session = Depends(get_db)):
    return insights_service.generate_insights(db)
