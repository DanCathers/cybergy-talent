"""Search service — filters the resume repository.

Supports free-text search (over the extracted raw text), skill filters (using
the denormalized ``skills_index``), and simple education/experience filters.
Kept intentionally straightforward and readable for learning purposes.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume
from app.schemas.api_schemas import SearchRequest


class SearchService:
    """Runs searches over stored resumes."""

    async def search(self, db: AsyncSession, request: SearchRequest) -> tuple[list[Resume], int]:
        """Return resumes matching the search request, plus a total count."""
        # Start with a base query and progressively add filters (AND logic).
        query = select(Resume)

        # 1) Free-text search over the extracted resume text (case-insensitive).
        if request.text:
            # ``ilike`` is a case-insensitive LIKE; %term% matches anywhere.
            query = query.where(Resume.raw_text.ilike(f"%{request.text}%"))

        # 2) Skill filters. Each required skill must appear in skills_index.
        for skill in request.skills:
            skill_lower = skill.lower().strip()
            if skill_lower:
                # PostgreSQL JSONB "contains" operator via SQLAlchemy's
                # ``.contains``: checks that the JSON array holds this value.
                query = query.where(Resume.skills_index.contains([skill_lower]))

        # 3) Education keyword. We search the extracted raw text, which reliably
        #    contains institution/degree names and is portable across databases.
        if request.education:
            query = query.where(Resume.raw_text.ilike(f"%{request.education}%"))

        # Count matches for pagination (wrap the filtered query in a subquery).
        count_subquery = query.subquery()
        total = await db.scalar(select(func.count()).select_from(count_subquery)) or 0

        # Apply ordering + pagination.
        offset = (request.page - 1) * request.page_size
        query = query.order_by(Resume.created_at.desc()).offset(offset).limit(request.page_size)
        result = await db.execute(query)
        items = list(result.scalars().all())
        return items, total

    async def aggregate_skills(self, db: AsyncSession) -> list[dict]:
        """Return every skill across all resumes with a frequency count.

        Used by the MCP ``/skills`` endpoint so agents can discover what talent
        is available in the repository.
        """
        # Load just the skills_index column from every resume.
        result = await db.execute(select(Resume.skills_index))
        # ``scalars().all()`` gives us a list of the JSONB arrays.
        all_indexes = result.scalars().all()

        # Tally occurrences of each skill using a plain dict.
        counts: dict[str, int] = {}
        for index in all_indexes:
            for skill in index or []:
                counts[skill] = counts.get(skill, 0) + 1

        # Sort by frequency (descending), then alphabetically for stability.
        ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        return [{"skill": name, "count": count} for name, count in ordered]


# Module-level singleton.
search_service = SearchService()
