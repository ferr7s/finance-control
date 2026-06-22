"""add sync_jobs table

Revision ID: 202606220001
Revises: 202606150001
Create Date: 2026-06-22
"""
import sqlalchemy as sa
from alembic import op

revision = "202606220001"
down_revision = "202606150001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sync_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("bank", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("transactions_synced", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sync_jobs_bank", "sync_jobs", ["bank"])
    op.create_index("ix_sync_jobs_started_at", "sync_jobs", ["started_at"])


def downgrade() -> None:
    op.drop_index("ix_sync_jobs_started_at", table_name="sync_jobs")
    op.drop_index("ix_sync_jobs_bank", table_name="sync_jobs")
    op.drop_table("sync_jobs")
