"""initial schema

Revision ID: 202606150001
Revises:
Create Date: 2026-06-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "202606150001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("type", sa.String(length=40), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("current_balance", sa.Numeric(14, 2), nullable=False),
        sa.Column("institution_name", sa.String(length=160), nullable=True),
        sa.Column("branch", sa.String(length=40), nullable=True),
        sa.Column("account_number_masked", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "credit_cards",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("brand", sa.String(length=80), nullable=True),
        sa.Column("limit_total", sa.Numeric(14, 2), nullable=True),
        sa.Column("limit_available", sa.Numeric(14, 2), nullable=True),
        sa.Column("closing_day", sa.Integer(), nullable=True),
        sa.Column("due_day", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "insights",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=40), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "agent_analyses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "credit_card_bills",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("credit_card_id", sa.Uuid(), nullable=False),
        sa.Column("reference_month", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("closing_date", sa.Date(), nullable=True),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["credit_card_id"], ["credit_cards.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "transactions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("external_id", sa.String(length=180), nullable=True),
        sa.Column("provider", sa.String(length=120), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=True),
        sa.Column("credit_card_id", sa.Uuid(), nullable=True),
        sa.Column("bill_id", sa.Uuid(), nullable=True),
        sa.Column("date", sa.DateTime(timezone=False), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("type", sa.String(length=40), nullable=False),
        sa.Column("payment_method", sa.String(length=40), nullable=True),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("subcategory", sa.String(length=120), nullable=True),
        sa.Column("merchant", sa.String(length=160), nullable=True),
        sa.Column("is_recurring", sa.Boolean(), nullable=False),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["bill_id"], ["credit_card_bills.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["credit_card_id"], ["credit_cards.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_transactions_provider_external_id",
        "transactions",
        ["provider", "external_id"],
        unique=True,
        postgresql_where=sa.text("external_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_transactions_provider_external_id", table_name="transactions")
    op.drop_table("transactions")
    op.drop_table("credit_card_bills")
    op.drop_table("agent_analyses")
    op.drop_table("insights")
    op.drop_table("credit_cards")
    op.drop_table("accounts")
