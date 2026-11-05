from fastapi import APIRouter, Depends, HTTPException, status
from src.presentation.schemas.auth_schemas import RegisterTenantRequest, LoginRequest, AuthTokenResponse
from src.presentation.api.dependencies import get_tenant_repository, get_user_repository
from src.application.use_cases.auth_use_cases import (
    RegisterTenantUseCase,
    RegisterTenantCommand,
    LoginUseCase,
)
from src.infrastructure.persistence.repositories.sqlalchemy_tenant_repository import SQLAlchemyTenantRepository
from src.infrastructure.persistence.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository

router = APIRouter(prefix="/auth", tags=["Authentication & Multi-Tenant Onboarding"])


@router.post("/register-tenant", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
async def register_tenant(
    data: RegisterTenantRequest,
    tenant_repo: SQLAlchemyTenantRepository = Depends(get_tenant_repository),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
):
    use_case = RegisterTenantUseCase(tenant_repo, user_repo)
    try:
        dto = await use_case.execute(
            RegisterTenantCommand(
                tenant_name=data.tenant_name,
                tenant_slug=data.tenant_slug,
                admin_email=data.admin_email,
                admin_password=data.admin_password,
                admin_full_name=data.admin_full_name,
            )
        )
        return dto
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=AuthTokenResponse)
async def login(
    data: LoginRequest,
    tenant_repo: SQLAlchemyTenantRepository = Depends(get_tenant_repository),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
):
    use_case = LoginUseCase(tenant_repo, user_repo)
    try:
        dto = await use_case.execute(
            email=data.email,
            password=data.password,
            tenant_slug=data.tenant_slug,
        )
        return dto
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
