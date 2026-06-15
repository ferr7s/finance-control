from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent_analysis import AgentAnalysis
from app.schemas.agent_analysis import AgentAnalysisCreate


def list_agent_analyses(db: Session) -> list[AgentAnalysis]:
    return list(db.scalars(select(AgentAnalysis).order_by(AgentAnalysis.created_at.desc())).all())


def get_agent_analysis(db: Session, analysis_id: UUID) -> AgentAnalysis | None:
    return db.get(AgentAnalysis, analysis_id)


def create_agent_analysis(db: Session, payload: AgentAnalysisCreate) -> AgentAnalysis:
    analysis = AgentAnalysis(
        source=payload.source,
        title=payload.title,
        content=payload.content,
        metadata_json=payload.metadata,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis
