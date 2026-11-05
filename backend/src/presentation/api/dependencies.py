from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db_session
from src.core.security import decode_access_token
from src.core.context import set_current_tenant_id, get_current_tenant_id
from src.infrastructure.persistence.repositories.sqlalchemy_tenant_repository import SQLAlchemyTenantRepository
from src.infrastructure.persistence.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.infrastructure.persistence.repositories.sqlalchemy_employee_repository import SQLAlchemyEmployeeRepository

security_scheme = HTTPBearer(auto_error=True)


async def get_tenant_repository(db: AsyncSession = Depends(get_db_session)) -> SQLAlchemyTenantRepository:
    return SQLAlchemyTenantRepository(db)


async def get_user_repository(db: AsyncSession = Depends(get_db_session)) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(db)


async def get_employee_repository(db: AsyncSession = Depends(get_db_session)) -> SQLAlchemyEmployeeRepository:
    return SQLAlchemyEmployeeRepository(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> Dict[str, Any]:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is missing tenant identifier",
        )

    # Set tenant context for the authenticated request
    set_current_tenant_id(tenant_id)
    return payload
