from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from src.core.config import settings
from src.core.context import get_current_tenant_id

engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DEBUG,
    future=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields an async database session configured with multi-tenant context.
    If a tenant ID exists in the async context, it configures PostgreSQL session local variable
    so Row-Level Security (RLS) policies apply automatically.
    """
    async with AsyncSessionLocal() as session:
        tenant_id = get_current_tenant_id()
        if tenant_id:
            # Set the tenant context in PostgreSQL session for RLS policies
            await session.execute(
                text("SET LOCAL app.current_tenant_id = :tenant_id"),
                {"tenant_id": tenant_id},
            )
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
