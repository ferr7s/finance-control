"""add email_sync_jobs table

Revision ID: 202606230001
Revises: 202606220001
Create Date: 2026-06-23
"""
import sqlalchemy as sa
from alembic import op

revision = "202606230001"
down_revision = "202606220001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "email_sync_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("imported", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ignored", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_sync_jobs_started_at", "email_sync_jobs", ["started_at"])


def downgrade() -> None:
    op.drop_index("ix_email_sync_jobs_started_at", table_name="email_sync_jobs")
    op.drop_table("email_sync_jobs")
