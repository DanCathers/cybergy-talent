"""Initial schema — create the resumes table.

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# Revision identifiers used by Alembic to order migrations.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the ``resumes`` table."""
    op.create_table(
        "resumes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("profile_name", sa.String(length=255), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("source_filename", sa.String(length=512), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        # JSONB stores the full HR Open Standards profile efficiently.
        sa.Column("profile", postgresql.JSONB(), nullable=False),
        sa.Column("skills_index", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    # An index on created_at speeds up the "newest first" listing query.
    op.create_index("ix_resumes_created_at", "resumes", ["created_at"])


def downgrade() -> None:
    """Drop the ``resumes`` table (reverse of upgrade)."""
    op.drop_index("ix_resumes_created_at", table_name="resumes")
    op.drop_table("resumes")
