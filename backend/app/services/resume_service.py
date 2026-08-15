"""Resume service — orchestrates upload -> parse -> AI map -> persist.

This is the business-logic layer that ties the parsers, the AI conversion
service, and the database together. Keeping this logic out of the API routers
follows Clean Architecture: routers stay thin, services hold the real work.
"""

from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume
from app.parsers.parser_factory import ParserFactory
from app.schemas.hr_open_standards import Identifier, PersonProfile
from app.services.conversion_service import conversion_service


class ResumeService:
    """High-level operations for creating and retrieving resumes."""

    async def create_from_upload(
        self,
        db: AsyncSession,
        *,
        file_bytes: bytes,
        filename: str,
        extension: str,
    ) -> Resume:
        """Parse an uploaded file, map it with AI, and store the result.

        The ``*`` in the signature forces the following arguments to be passed
        by keyword (e.g. ``filename=...``), which makes call sites self-documenting.

        Args:
            db: The active async database session.
            file_bytes: Raw bytes of the uploaded resume.
            filename: Original file name (for display + provenance).
            extension: Validated file extension (".pdf" or ".docx").

        Returns:
            The newly persisted :class:`Resume` ORM object.
        """
        # 1) Pick the parsing strategy for this file type and extract text.
        parser = ParserFactory.get_parser(extension)
        raw_text = await parser.extract_text(file_bytes)

        # 2) Ask the AI service to map the text to an HR Open profile.
        profile = await conversion_service.map_resume_text(raw_text)

        # 3) Build denormalized helper fields for listing/search.
        full_name = self._derive_full_name(profile)
        skills_index = self._derive_skills_index(profile)

        # 4) Create and persist the ORM row.
        resume = Resume(
            profile_name=profile.profileName or full_name,
            full_name=full_name,
            source_filename=filename,
            raw_text=raw_text,
            # Store the profile as a plain dict in the JSONB column.
            profile=profile.model_dump(exclude_none=True),
            skills_index=skills_index,
        )
        db.add(resume)  # stage the insert
        await db.commit()  # write to the database
        await db.refresh(resume)  # reload DB-generated fields (id, timestamps)
        return resume

    async def get(self, db: AsyncSession, resume_id: str) -> Resume | None:
        """Fetch a single resume by id, or ``None`` if it doesn't exist."""
        # ``select`` builds a query; ``scalar_one_or_none`` returns 0 or 1 row.
        result = await db.execute(select(Resume).where(Resume.id == resume_id))
        return result.scalar_one_or_none()

    async def list(
        self, db: AsyncSession, *, page: int = 1, page_size: int = 20
    ) -> tuple[list[Resume], int]:
        """Return a page of resumes plus the total count.

        Returns a tuple ``(items, total)`` so the caller can build pagination.
        """
        # Count the total number of rows for pagination metadata.
        total = await db.scalar(select(func.count()).select_from(Resume)) or 0

        # ``offset``/``limit`` implement pagination; newest first.
        offset = (page - 1) * page_size
        result = await db.execute(
            select(Resume).order_by(Resume.created_at.desc()).offset(offset).limit(page_size)
        )
        # ``scalars().all()`` returns the ORM objects (not row tuples).
        items = list(result.scalars().all())
        return items, total

    async def delete(self, db: AsyncSession, resume_id: str) -> bool:
        """Delete a resume by id. Returns True if a row was removed."""
        result = await db.execute(delete(Resume).where(Resume.id == resume_id))
        await db.commit()
        # ``rowcount`` tells us how many rows the DELETE affected.
        return (result.rowcount or 0) > 0

    def to_profile(self, resume: Resume) -> PersonProfile:
        """Rebuild a :class:`PersonProfile` from a stored resume row.

        Used by the download endpoints and converters. We re-validate the
        stored dict so downstream code always works with a typed model.
        """
        profile = PersonProfile.model_validate(resume.profile or {})
        # Ensure the id reflects the database id for traceability.
        # HR Open requires ``id`` to be an IdentifierType object ({"value": ...}),
        # so we wrap the raw database id explicitly. (Pydantic does not run the
        # field validator on plain attribute assignment, so we build the object
        # ourselves rather than assigning a bare string.)
        profile.id = Identifier(value=str(resume.id))
        return profile

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _derive_full_name(profile: PersonProfile) -> str | None:
        """Compute a display name from the profile's name parts."""
        if profile.name is None:
            return None
        if profile.name.formattedName:
            return profile.name.formattedName
        # Join given + family when a formatted name isn't provided.
        parts = [profile.name.given, profile.name.family]
        joined = " ".join(p for p in parts if p)
        return joined or None

    @staticmethod
    def _derive_skills_index(profile: PersonProfile) -> list[str]:
        """Flatten skills into a lower-cased list for fast filtering."""
        # A list comprehension collects every non-empty competency name.
        return [q.competencyName.lower() for q in profile.qualifications if q.competencyName]


# Module-level singleton for convenient importing.
resume_service = ResumeService()
