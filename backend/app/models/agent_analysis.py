from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, utcnow
from app.models.mixins import UUIDPrimaryKeyMixin


class AgentAnalysis(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "agent_analyses"

    source: Mapped[str] = mapped_column(String(80), default="hermes", nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
