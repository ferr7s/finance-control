from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, JSON, Numeric, String, Text, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Transaction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "transactions"
    __table_args__ = (
        Index(
            "uq_transactions_provider_external_id",
            "provider",
            "external_id",
            unique=True,
            postgresql_where=text("external_id IS NOT NULL"),
        ),
    )

    external_id: Mapped[str | None] = mapped_column(String(180))
    provider: Mapped[str] = mapped_column(String(120), nullable=False)
    account_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("accounts.id", ondelete="SET NULL"))
    credit_card_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("credit_cards.id", ondelete="SET NULL"),
    )
    bill_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("credit_card_bills.id", ondelete="SET NULL"),
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    type: Mapped[str] = mapped_column(String(40), nullable=False)
    payment_method: Mapped[str | None] = mapped_column(String(40))
    category: Mapped[str | None] = mapped_column(String(120))
    subcategory: Mapped[str | None] = mapped_column(String(120))
    merchant: Mapped[str | None] = mapped_column(String(160))
    is_recurring: Mapped[bool] = mapped_column(default=False, nullable=False)
    raw_data: Mapped[dict | None] = mapped_column(JSONB().with_variant(JSON(), "sqlite"))

    account = relationship("Account", back_populates="transactions")
    credit_card = relationship("CreditCard", back_populates="transactions")
    bill = relationship("CreditCardBill", back_populates="transactions")
