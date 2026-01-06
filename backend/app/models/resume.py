"""SQLAlchemy ORM model for a stored resume.

We store the full HR Open Standards profile as JSONB (a binary JSON column in
PostgreSQL) so we don't have to spread the deeply-nested resume across dozens
of relational tables. A handful of scalar columns are duplicated out of the
JSON for fast listing, searching, and sorting.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _utcnow() -> datetime:
    """Return the current UTC time (timezone-aware).

    Defined as a helper so it can be used as a column default callable.
    """
    return datetime.now(timezone.utc)


class Resume(Base):
    """A single uploaded + AI-converted resume."""

    __tablename__ = "resumes"

    # Primary key: a random UUID stored as a string. ``default`` runs a lambda
    # that generates a new UUID for each inserted row.
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # A human-friendly label for the profile (falls back to the person's name).
    profile_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # The person's full name, denormalized for quick display/search.
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # The original uploaded file name (e.g. "jane_doe_cv.pdf").
    source_filename: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # The raw text extracted from the file, kept for search and re-processing.
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # The complete HR Open Standards profile, stored as JSONB.
    profile: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # A flattened, lower-cased list of skills for efficient skill filtering.
    # Stored as JSONB array of strings.
    skills_index: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # Timestamps. ``default`` sets the value on insert.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        """Readable representation shown in logs / the debugger."""
        return f"<Resume id={self.id!r} name={self.full_name!r}>"
