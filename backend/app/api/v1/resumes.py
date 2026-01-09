"""Resume REST endpoints: upload, list, get, delete, and download.

This is the presentation layer. Endpoints stay thin: they validate input,
delegate to the service layer, and shape the HTTP response.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.converters.converter_factory import ConverterFactory
from app.core.database import get_db
from app.core.security import limiter, validate_upload
from app.schemas.api_schemas import (
    ResumeDetail,
    ResumeListResponse,
    ResumeSummary,
    UploadResponse,
)
from app.services.resume_service import resume_service

# ``prefix`` puts every route below under /api/v1/resumes. ``tags`` groups them
# in the auto-generated Swagger docs.
router = APIRouter(prefix="/api/v1/resumes", tags=["resumes"])


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a PDF/DOCX resume, extract, AI-map, and store it.",
)
@limiter.limit("10/minute")  # rate limit: max 10 uploads per minute per IP
async def upload_resume(
    request: Request,  # required by slowapi to read the client IP
    file: UploadFile,
    db: AsyncSession = Depends(get_db),  # dependency-injected DB session
) -> UploadResponse:
    """Accept a resume file, validate it, and run the conversion pipeline."""
    # Read the file contents into memory (uploads are capped at 10 MB).
    file_bytes = await file.read()

    # Validate extension + MIME + size. Raises ValueError on any problem.
    try:
        extension = validate_upload(
            filename=file.filename or "",
            mime_type=file.content_type or "",
            size_bytes=len(file_bytes),
        )
    except ValueError as exc:
        # Translate a domain error into a clean 400 Bad Request.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    # Delegate the heavy lifting (parse -> AI map -> persist) to the service.
    resume = await resume_service.create_from_upload(
        db,
        file_bytes=file_bytes,
        filename=file.filename or "resume",
        extension=extension,
    )

    return UploadResponse(
        id=resume.id,
        message="Resume uploaded and mapped to HR Open Standards successfully.",
        profile=resume_service.to_profile(resume),
    )


@router.get("/", response_model=ResumeListResponse, summary="List stored resumes.")
async def list_resumes(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> ResumeListResponse:
    """Return a paginated list of resume summaries (newest first)."""
    items, total = await resume_service.list(db, page=page, page_size=page_size)
    # Build lightweight summaries for the list view.
    summaries = [
        ResumeSummary(
            id=r.id,
            profile_name=r.profile_name,
            full_name=r.full_name,
            top_skills=(r.skills_index or [])[:8],  # first few skills as a teaser
            source_filename=r.source_filename,
            created_at=r.created_at,
        )
        for r in items
    ]
    return ResumeListResponse(items=summaries, total=total, page=page, page_size=page_size)


@router.get("/{resume_id}", response_model=ResumeDetail, summary="Get one resume.")
async def get_resume(resume_id: str, db: AsyncSession = Depends(get_db)) -> ResumeDetail:
    """Return the full detail (including HR Open profile) for one resume."""
    resume = await resume_service.get(db, resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return ResumeDetail(
        id=resume.id,
        profile_name=resume.profile_name,
        full_name=resume.full_name,
        top_skills=(resume.skills_index or [])[:8],
        source_filename=resume.source_filename,
        created_at=resume.created_at,
        profile=resume_service.to_profile(resume),
    )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(resume_id: str, db: AsyncSession = Depends(get_db)) -> Response:
    """Delete a resume by id. Returns 204 No Content on success."""
    deleted = await resume_service.delete(db, resume_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Resume not found.")
    # 204 responses carry no body.
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{resume_id}/download/{fmt}",
    summary="Download a resume as HR Open Standards JSON or XML.",
)
async def download_resume(resume_id: str, fmt: str, db: AsyncSession = Depends(get_db)) -> Response:
    """Serialize a resume with the requested converter and stream it as a file.

    ``fmt`` must be "json" or "xml". The converter embeds the required HR Open
    Standards attribution/compliance notices in the output.
    """
    resume = await resume_service.get(db, resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found.")

    # Pick the converter via the factory; unknown formats -> 400.
    try:
        converter = ConverterFactory.get_converter(fmt)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    profile = resume_service.to_profile(resume)
    body = converter.convert(profile)

    # Suggest a download filename via the Content-Disposition header.
    filename = f"resume_{resume_id}{converter.file_extension}"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=body, media_type=converter.media_type, headers=headers)
