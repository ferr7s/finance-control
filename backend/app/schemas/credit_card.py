from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreditCardBase(BaseModel):
    provider: str
    name: str
    brand: str | None = None
    limit_total: Decimal | None = None
    limit_available: Decimal | None = None
    closing_day: int | None = None
    due_day: int | None = None


class CreditCardCreate(CreditCardBase):
    pass


class CreditCardUpdate(BaseModel):
    provider: str | None = None
    name: str | None = None
    brand: str | None = None
    limit_total: Decimal | None = None
    limit_available: Decimal | None = None
    closing_day: int | None = None
    due_day: int | None = None


class CreditCardRead(CreditCardBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
