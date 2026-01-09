"""Search endpoint for the resume repository."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.api_schemas import (
    ResumeListResponse,
    ResumeSummary,
    SearchRequest,
)
from app.services.search_service import search_service

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.post(
    "/",
    response_model=ResumeListResponse,
    summary="Search resumes by text, skills, education, and experience.",
)
async def search_resumes(
    request: SearchRequest, db: AsyncSession = Depends(get_db)
) -> ResumeListResponse:
    """Run a structured search and return paginated summaries."""
    items, total = await search_service.search(db, request)
    summaries = [
        ResumeSummary(
            id=r.id,
            profile_name=r.profile_name,
            full_name=r.full_name,
            top_skills=(r.skills_index or [])[:8],
            source_filename=r.source_filename,
            created_at=r.created_at,
        )
        for r in items
    ]
    return ResumeListResponse(
        items=summaries, total=total, page=request.page, page_size=request.page_size
    )
