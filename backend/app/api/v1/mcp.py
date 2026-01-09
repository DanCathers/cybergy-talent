"""MCP-compatible agent query endpoints.

MCP (the Model Context Protocol) is a convention for exposing "tools" that AI
agents can discover and call. These endpoints let an agent:

  * discover the available tools and their input schemas (``/mcp/schema``),
  * query the repository in natural language or by skills (``/mcp/query``),
  * fetch a single resume as full HR Open Standards JSON (``/mcp/resume/{id}``),
  * list the aggregated skills across all resumes (``/mcp/skills``).

Every response uses the consistent :class:`MCPEnvelope` shape
(``status`` / ``data`` / ``metadata``) so agents can parse results uniformly.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.api_schemas import (
    MCPEnvelope,
    MCPQueryRequest,
    SearchRequest,
)
from app.schemas.hr_open_standards import HR_OPEN_VERSION
from app.services.resume_service import resume_service
from app.services.search_service import search_service

router = APIRouter(prefix="/api/v1/mcp", tags=["mcp"])


@router.get("/schema", response_model=MCPEnvelope, summary="Discover MCP tools.")
async def mcp_schema() -> MCPEnvelope:
    """Return a machine-readable description of the tools this API exposes.

    An agent calls this first to learn what it can do and how to call each tool.
    """
    tools = [
        {
            "name": "query_resumes",
            "description": "Search the resume repository by natural language or skills.",
            "method": "POST",
            "path": "/api/v1/mcp/query",
            "input_schema": {
                "query": "string (optional natural-language query)",
                "skills": "string[] (optional required skills)",
                "limit": "integer (1-50, default 10)",
            },
        },
        {
            "name": "get_resume",
            "description": "Fetch one resume as full HR Open Standards JSON.",
            "method": "GET",
            "path": "/api/v1/mcp/resume/{id}",
        },
        {
            "name": "list_skills",
            "description": "List all skills across the repository with counts.",
            "method": "GET",
            "path": "/api/v1/mcp/skills",
        },
    ]
    return MCPEnvelope(
        status="ok",
        data={"tools": tools},
        metadata={
            "service": "Cybergy Talent MCP",
            "standard": "HR Open Standards",
            "version": HR_OPEN_VERSION,
        },
    )


@router.post("/query", response_model=MCPEnvelope, summary="Agent query tool.")
async def mcp_query(request: MCPQueryRequest, db: AsyncSession = Depends(get_db)) -> MCPEnvelope:
    """Answer an agent's query with matching resumes.

    We translate the MCP request into our internal :class:`SearchRequest`. The
    free-text ``query`` maps to a text search; ``skills`` maps to skill filters.
    """
    search = SearchRequest(
        text=request.query,
        skills=request.skills,
        page=1,
        page_size=request.limit,
    )
    items, total = await search_service.search(db, search)

    # Return compact result objects that are easy for an agent to reason over.
    results = [
        {
            "id": r.id,
            "full_name": r.full_name,
            "profile_name": r.profile_name,
            "skills": r.skills_index or [],
        }
        for r in items
    ]
    return MCPEnvelope(
        status="ok",
        data={"results": results},
        metadata={"total_matches": total, "returned": len(results)},
    )


@router.get(
    "/resume/{resume_id}",
    response_model=MCPEnvelope,
    summary="Get one resume as HR Open Standards JSON.",
)
async def mcp_get_resume(resume_id: str, db: AsyncSession = Depends(get_db)) -> MCPEnvelope:
    """Return a single resume's full profile, including attribution notices."""
    resume = await resume_service.get(db, resume_id)
    if resume is None:
        # For MCP we return a structured error envelope rather than raising,
        # so agents get a consistent shape they can branch on.
        return MCPEnvelope(
            status="error",
            data=None,
            metadata={"message": f"No resume found with id {resume_id}."},
        )

    profile = resume_service.to_profile(resume)
    # ``with_attribution`` embeds the required HR Open Standards notices.
    return MCPEnvelope(
        status="ok",
        data=profile.with_attribution(),
        metadata={"id": resume_id, "standard": "HR Open Standards", "version": HR_OPEN_VERSION},
    )


@router.get("/skills", response_model=MCPEnvelope, summary="Aggregate all skills.")
async def mcp_skills(db: AsyncSession = Depends(get_db)) -> MCPEnvelope:
    """Return every skill across the repository with occurrence counts."""
    skills = await search_service.aggregate_skills(db)
    return MCPEnvelope(
        status="ok",
        data={"skills": skills},
        metadata={"unique_skills": len(skills)},
    )
