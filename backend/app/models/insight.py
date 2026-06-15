from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, utcnow
from app.models.mixins import UUIDPrimaryKeyMixin


class Insight(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "insights"

    type: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(40), default="info", nullable=False)
    source: Mapped[str] = mapped_column(String(80), default="system", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
