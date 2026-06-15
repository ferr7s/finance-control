from decimal import Decimal

from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class CreditCard(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "credit_cards"

    provider: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(80))
    limit_total: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    limit_available: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    closing_day: Mapped[int | None] = mapped_column(Integer)
    due_day: Mapped[int | None] = mapped_column(Integer)

    bills = relationship("CreditCardBill", back_populates="credit_card", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="credit_card")
