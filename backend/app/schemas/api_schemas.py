"""API request/response schemas.

These Pydantic models describe the shapes that flow in and out of the REST and
MCP endpoints. They are separate from the HR Open Standards domain models so
that the public API contract can evolve independently of the data standard.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.hr_open_standards import PersonProfile


class ResumeSummary(BaseModel):
    """A lightweight view of a stored resume, used in list/search results."""

    id: str
    profile_name: str | None = None
    full_name: str | None = None
    top_skills: list[str] = Field(default_factory=list)
    source_filename: str | None = None
    created_at: datetime

    # ``from_attributes`` lets us build this model directly from an ORM object.
    model_config = {"from_attributes": True}


class ResumeDetail(ResumeSummary):
    """A full resume view including the complete HR Open Standards profile."""

    profile: PersonProfile


class ResumeListResponse(BaseModel):
    """Paginated list of resume summaries."""

    items: list[ResumeSummary]
    total: int
    page: int
    page_size: int


class SearchRequest(BaseModel):
    """Structured search filters for the repository.

    All fields are optional; provided filters are combined with AND logic.
    """

    text: str | None = Field(default=None, description="Free-text search across the resume.")
    skills: list[str] = Field(default_factory=list, description="Required skill names.")
    min_experience_years: float | None = Field(
        default=None, description="Minimum total years of experience."
    )
    education: str | None = Field(default=None, description="Degree or institution keyword.")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class UploadResponse(BaseModel):
    """Returned after a successful upload + AI conversion."""

    id: str
    message: str
    profile: PersonProfile


# ---------------------------------------------------------------------------
# MCP (Model Context Protocol) envelope
# ---------------------------------------------------------------------------
class MCPEnvelope(BaseModel):
    """Consistent MCP response envelope with status/data/metadata.

    All MCP endpoints return this shape so that AI agents can rely on a single,
    predictable structure regardless of which tool they call.
    """

    status: str = Field(default="ok", description="'ok' or 'error'.")
    data: Any = Field(default=None, description="The tool's result payload.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extra context.")


class MCPQueryRequest(BaseModel):
    """Input for the MCP natural-language / structured query endpoint."""

    query: str | None = Field(default=None, description="Natural-language query.")
    skills: list[str] = Field(default_factory=list, description="Optional structured filter.")
    limit: int = Field(default=10, ge=1, le=50)
