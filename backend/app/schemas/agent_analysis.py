from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AgentAnalysisCreate(BaseModel):
    source: str = "hermes"
    title: str
    content: str
    metadata: dict | None = None


class AgentAnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    source: str
    title: str
    content: str
    metadata: dict | None = Field(default=None, alias="metadata_json")
    created_at: datetime
