"""Alembic migration environment.

Alembic manages incremental, version-controlled database schema changes. This
env loads the async engine + models and runs migrations. The database URL comes
from the application settings (i.e. the environment), never hard-coded.
"""

from __future__ import annotations

import asyncio

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

# Import settings and the declarative Base so Alembic can see our tables.
from app.core.config import settings
from app.core.database import Base

# Importing the model registers its table on ``Base.metadata`` so Alembic's
# autogenerate can detect schema changes.
from app.models import resume  # noqa: F401

# ``target_metadata`` tells Alembic which tables it should manage.
target_metadata = Base.metadata


def do_run_migrations(connection) -> None:
    """Configure the migration context and run migrations for a connection."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations within it."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async with engine.connect() as connection:
        # ``run_sync`` bridges Alembic's synchronous API into the async engine.
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_online() -> None:
    """Entry point for 'online' migrations (against a live database)."""
    asyncio.run(run_async_migrations())


# Alembic calls one of these depending on mode. We only support online mode.
run_migrations_online()
