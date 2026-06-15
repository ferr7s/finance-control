from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InsightCreate(BaseModel):
    type: str
    title: str
    content: str
    severity: str = "info"
    source: str = "system"


class InsightRead(InsightCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
