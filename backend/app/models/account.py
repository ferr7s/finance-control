from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Account(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "accounts"

    provider: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    type: Mapped[str] = mapped_column(String(40), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="BRL", nullable=False)
    current_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    institution_name: Mapped[str | None] = mapped_column(String(160))
    branch: Mapped[str | None] = mapped_column(String(40))
    account_number_masked: Mapped[str | None] = mapped_column(String(80))

    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
