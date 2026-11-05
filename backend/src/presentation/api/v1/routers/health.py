from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.core.database import get_db_session
from src.core.context import get_current_tenant_id

router = APIRouter(prefix="/health", tags=["Health & Diagnostic"])


@router.get("")
async def health_check():
    return {
        "status": "healthy",
        "current_tenant": get_current_tenant_id() or "system",
    }


@router.get("/db")
async def db_health_check(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(text("SELECT 1"))
    return {
        "database": "connected" if result.scalar() == 1 else "unhealthy",
        "current_tenant": get_current_tenant_id() or "system",
    }
