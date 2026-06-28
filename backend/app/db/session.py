from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

# Create the async database engine
# settings.database_url_async resolves postgresql+asyncpg connection
engine = create_async_engine(
    settings.database_url_async,
    echo=True,  # Set to True to log generated SQL statements (useful for debugging)
    future=True
)

# Create sessionmaker factory for creating AsyncSession instances
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency yielding database sessions.
    Ensures sessions are properly closed after request completion.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
