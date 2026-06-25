from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, utcnow
from app.models.mixins import UUIDPrimaryKeyMixin


class EmailSyncJob(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "email_sync_jobs"

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    imported: Mapped[int] = mapped_column(nullable=False, default=0)
    ignored: Mapped[int] = mapped_column(nullable=False, default=0)
    errors: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
