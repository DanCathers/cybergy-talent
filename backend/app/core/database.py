"""Async SQLAlchemy database setup.

This module wires up:
  * an async engine (the low-level connection pool to PostgreSQL),
  * an async session factory (creates short-lived DB sessions per request),
  * a declarative ``Base`` class that all ORM models inherit from,
  * a FastAPI dependency (``get_db``) that yields a session and cleans it up.

Everything is async so that the FastAPI event loop is never blocked while
waiting on the database.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all ORM models.

    SQLAlchemy 2.0 uses a typed ``DeclarativeBase``; every model subclasses it
    so that SQLAlchemy can collect their table metadata in one place.
    """


# ``create_async_engine`` builds the async connection pool. ``echo=False``
# keeps SQL out of the logs; flip to True temporarily when debugging queries.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # transparently checks connections are alive before use
)

# The session factory. ``expire_on_commit=False`` keeps ORM objects usable
# after a commit (handy when returning them from an endpoint).
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides a database session per request.

    ``async with`` guarantees the session is closed even if the request raises.
    ``yield`` hands the session to the endpoint; code after the yield runs on
    the way back out (cleanup).
    """
    async with AsyncSessionLocal() as session:  # context manager -> auto-close
        yield session


async def init_db() -> None:
    """Create all tables that don't yet exist.

    Convenient for local development and tests. In production you should use
    Alembic migrations instead (see the ``alembic/`` directory).
    """
    # Importing here avoids a circular import at module load time.
    from app.models import resume  # noqa: F401  (import registers the model)

    async with engine.begin() as conn:
        # ``run_sync`` lets us call the synchronous ``create_all`` inside the
        # async connection context.
        await conn.run_sync(Base.metadata.create_all)
