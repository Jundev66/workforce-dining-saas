from fastapi import Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.contexts.iam.infrastructure.persistence.repositories import (
    SQLAlchemyTenantRepository,
    SQLAlchemyUserRepository,
)
from src.contexts.iam.application.use_cases.login_use_case import LoginUseCase
from src.contexts.iam.application.dtos import LoginCommand, AuthResponseDTO
from src.contexts.iam.presentation.controllers.register_tenant_controller import (
    get_tenant_repo,
    get_user_repo,
)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_slug: str | None = None


class LoginController:
    """Single-Action Controller: Handles user credentials validation and token issuance."""

    @staticmethod
    async def handle(
        data: LoginRequest,
        tenant_repo: SQLAlchemyTenantRepository = Depends(get_tenant_repo),
        user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
    ) -> AuthResponseDTO:
        use_case = LoginUseCase(tenant_repo, user_repo)
        try:
            return await use_case.execute(
                LoginCommand(
                    email=data.email,
                    password=data.password,
                    tenant_slug=data.tenant_slug,
                )
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
