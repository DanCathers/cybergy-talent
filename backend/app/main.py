"""FastAPI application entry point for Cybergy Talent.

Wires together configuration, middleware (CORS + security headers), rate
limiting, the database lifecycle, and all API routers.

Run locally with:
    uvicorn app.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1 import convert, mcp, resumes, search
from app.core.config import settings
from app.core.database import init_db
from app.core.security import SecurityHeadersMiddleware, limiter
from app.schemas.hr_open_standards import (
    HR_OPEN_ATTRIBUTION,
    HR_OPEN_COMPLIANCE,
    HR_OPEN_VERSION,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler (startup + shutdown).

    Code before ``yield`` runs on startup; code after runs on shutdown. Using
    a lifespan context manager is the modern FastAPI replacement for the old
    ``@app.on_event`` hooks.
    """
    # On startup: ensure tables exist (dev convenience; use Alembic in prod).
    await init_db()
    yield
    # On shutdown: nothing to clean up explicitly (engine disposes itself).


# Create the FastAPI application with rich metadata for the auto docs.
app = FastAPI(
    title="Cybergy Talent API",
    description=(
        "AI-agent-queryable resume intelligence API implementing "
        "HR Open Standards v"
        + HR_OPEN_VERSION
        + ".\n\n"
        + HR_OPEN_ATTRIBUTION
        + "\n\n"
        + HR_OPEN_COMPLIANCE
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# --- Rate limiting ---
# Attach the shared limiter to the app state and register the 429 handler.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Middleware ---
# CORS lets the Next.js frontend (a different origin) call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Security headers on every response (added last so it runs first outbound).
app.add_middleware(SecurityHeadersMiddleware)

# --- Routers ---
# Each router bundles related endpoints; ``include_router`` mounts them.
app.include_router(resumes.router)
app.include_router(convert.router)
app.include_router(search.router)
app.include_router(mcp.router)


@app.get("/health", tags=["meta"], summary="Liveness/health probe.")
async def health() -> dict:
    """Simple health check used by Docker/monitoring to verify the app is up."""
    return {"status": "ok", "service": "cybergy-talent", "version": app.version}


@app.get("/", tags=["meta"], summary="API root with links and attribution.")
async def root() -> dict:
    """Return a friendly landing payload with docs links and attribution."""
    return {
        "name": "Cybergy Talent API",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "mcp_schema": "/api/v1/mcp/schema",
        "_attribution": HR_OPEN_ATTRIBUTION,
        "_compliance": HR_OPEN_COMPLIANCE,
    }
