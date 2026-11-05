from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.database import get_db_session
from src.contexts.iam.infrastructure.persistence.repositories import (
    SQLAlchemyTenantRepository,
    SQLAlchemyUserRepository,
)
from src.contexts.iam.application.use_cases import (
    RegisterTenantUseCase,
    LoginUseCase,
)
from src.contexts.iam.application.dtos import RegisterTenantCommand, LoginCommand, AuthResponseDTO

router = APIRouter(prefix="/auth", tags=["IAM - Multi-Tenant Authentication"])


class RegisterTenantRequest(BaseModel):
    tenant_name: str = Field(..., min_length=2, max_length=100)
    tenant_slug: str = Field(..., min_length=2, max_length=50)
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=8)
    admin_full_name: str = Field(..., min_length=2, max_length=150)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_slug: str | None = None


def get_tenant_repo(db: AsyncSession = Depends(get_db_session)) -> SQLAlchemyTenantRepository:
    return SQLAlchemyTenantRepository(db)


def get_user_repo(db: AsyncSession = Depends(get_db_session)) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(db)


@router.post("/register-tenant", response_model=AuthResponseDTO, status_code=status.HTTP_201_CREATED)
async def register_tenant(
    data: RegisterTenantRequest,
    tenant_repo: SQLAlchemyTenantRepository = Depends(get_tenant_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
):
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


@router.post("/login", response_model=AuthResponseDTO)
async def login(
    data: LoginRequest,
    tenant_repo: SQLAlchemyTenantRepository = Depends(get_tenant_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
):
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
