from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class CreditCardBill(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "credit_card_bills"

    credit_card_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("credit_cards.id", ondelete="CASCADE"),
        nullable=False,
    )
    reference_month: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date)
    closing_date: Mapped[date | None] = mapped_column(Date)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="unknown", nullable=False)

    credit_card = relationship("CreditCard", back_populates="bills")
    transactions = relationship("Transaction", back_populates="bill")
