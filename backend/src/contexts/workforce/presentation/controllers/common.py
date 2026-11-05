from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.database import get_db_session
from src.shared.infrastructure.security import decode_access_token
from src.shared.infrastructure.tenant_context import set_current_tenant_id
from src.contexts.workforce.infrastructure.persistence.repositories import SQLAlchemyEmployeeRepository

security_scheme = HTTPBearer(auto_error=True)


def get_employee_repo(db: AsyncSession = Depends(get_db_session)) -> SQLAlchemyEmployeeRepository:
    return SQLAlchemyEmployeeRepository(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> Dict[str, Any]:
    payload = decode_access_token(credentials.credentials)
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
            detail="Token missing tenant context",
        )
    set_current_tenant_id(tenant_id)
    return payload
