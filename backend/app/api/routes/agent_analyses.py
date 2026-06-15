from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.agent_analysis import AgentAnalysisRead
from app.services import agent_analyses_service

router = APIRouter(prefix="/api/agent-analyses", tags=["agent analyses"])


@router.get("", response_model=list[AgentAnalysisRead])
def list_agent_analyses(db: Session = Depends(get_db)):
    return agent_analyses_service.list_agent_analyses(db)


@router.get("/{analysis_id}", response_model=AgentAnalysisRead)
def get_agent_analysis(analysis_id: UUID, db: Session = Depends(get_db)):
    analysis = agent_analyses_service.get_agent_analysis(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Agent analysis not found")
    return analysis
