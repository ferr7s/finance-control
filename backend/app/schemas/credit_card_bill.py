from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreditCardBillBase(BaseModel):
    reference_month: date
    due_date: date | None = None
    closing_date: date | None = None
    amount: Decimal = Decimal("0.00")
    status: str = "unknown"


class CreditCardBillCreate(CreditCardBillBase):
    pass


class CreditCardBillUpdate(BaseModel):
    reference_month: date | None = None
    due_date: date | None = None
    closing_date: date | None = None
    amount: Decimal | None = None
    status: str | None = None


class CreditCardBillRead(CreditCardBillBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    credit_card_id: UUID
    created_at: datetime
    updated_at: datetime
