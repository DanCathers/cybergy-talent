"""Standalone conversion endpoint.

Lets a client convert raw resume text to an HR Open Standards profile WITHOUT
persisting it — handy for previews, testing, and stateless integrations.
"""

from __future__ import annotations

from fastapi import APIRouter, Body

from app.schemas.hr_open_standards import PersonProfile
from app.services.conversion_service import conversion_service

router = APIRouter(prefix="/api/v1/convert", tags=["convert"])


@router.post(
    "/text",
    response_model=PersonProfile,
    summary="Map raw resume text to an HR Open Standards profile (no storage).",
)
async def convert_text(
    # ``Body(..., embed=True)`` expects {"text": "..."} in the request body.
    text: str = Body(..., embed=True, description="Raw resume text to map."),
) -> PersonProfile:
    """Run only the AI mapping step and return the structured profile."""
    return await conversion_service.map_resume_text(text)
