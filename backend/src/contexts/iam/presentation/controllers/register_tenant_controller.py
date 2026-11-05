from fastapi import Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.database import get_db_session
from src.contexts.iam.infrastructure.persistence.repositories import (
    SQLAlchemyTenantRepository,
    SQLAlchemyUserRepository,
)
from src.contexts.iam.application.use_cases.register_tenant_use_case import RegisterTenantUseCase
from src.contexts.iam.application.dtos import RegisterTenantCommand, AuthResponseDTO


class RegisterTenantRequest(BaseModel):
    tenant_name: str = Field(..., min_length=2, max_length=100)
    tenant_slug: str = Field(..., min_length=2, max_length=50)
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=8)
    admin_full_name: str = Field(..., min_length=2, max_length=150)


def get_tenant_repo(db: AsyncSession = Depends(get_db_session)) -> SQLAlchemyTenantRepository:
    return SQLAlchemyTenantRepository(db)


def get_user_repo(db: AsyncSession = Depends(get_db_session)) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(db)


class RegisterTenantController:
    """Single-Action Controller: Handles tenant onboarding and admin account creation."""

    @staticmethod
    async def handle(
        data: RegisterTenantRequest,
        tenant_repo: SQLAlchemyTenantRepository = Depends(get_tenant_repo),
        user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
    ) -> AuthResponseDTO:
        use_case = RegisterTenantUseCase(tenant_repo, user_repo)
        try:
            return await use_case.execute(
                RegisterTenantCommand(
                    tenant_name=data.tenant_name,
                    tenant_slug=data.tenant_slug,
                    admin_email=data.admin_email,
                    admin_password=data.admin_password,
                    admin_full_name=data.admin_full_name,
                )
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
