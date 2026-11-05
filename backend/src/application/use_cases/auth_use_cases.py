from dataclasses import dataclass
from typing import Optional
from src.domain.models.tenant import Tenant
from src.domain.models.user import User, UserRole
from src.domain.ports.tenant_repository import TenantRepository
from src.domain.ports.user_repository import UserRepository
from src.core.security import hash_password, verify_password, create_access_token


@dataclass
class RegisterTenantCommand:
    tenant_name: str
    tenant_slug: str
    admin_email: str
    admin_password: str
    admin_full_name: str


@dataclass
class AuthResponseDTO:
    access_token: str
    token_type: str
    user_id: str
    tenant_id: str
    role: str
    full_name: str
    email: str


class RegisterTenantUseCase:
    def __init__(
        self,
        tenant_repo: TenantRepository,
        user_repo: UserRepository,
    ):
        self.tenant_repo = tenant_repo
        self.user_repo = user_repo

    async def execute(self, cmd: RegisterTenantCommand) -> AuthResponseDTO:
        existing_tenant = await self.tenant_repo.get_by_slug(cmd.tenant_slug)
        if existing_tenant:
            raise ValueError(f"A tenant with slug '{cmd.tenant_slug}' already exists")

        # 1. Create tenant
        tenant = Tenant.create(name=cmd.tenant_name, slug=cmd.tenant_slug)
        created_tenant = await self.tenant_repo.create(tenant)

        # 2. Create admin user
        hashed_pwd = hash_password(cmd.admin_password)
        admin_user = User.create(
            tenant_id=created_tenant.id,
            email=cmd.admin_email,
            hashed_password=hashed_pwd,
            full_name=cmd.admin_full_name,
            role=UserRole.ADMIN,
        )
        created_user = await self.user_repo.create(admin_user)

        # 3. Generate token
        token = create_access_token(
            subject=created_user.id,
            tenant_id=created_tenant.id,
            role=created_user.role.value,
            extra_claims={"tenant_slug": created_tenant.slug, "full_name": created_user.full_name},
        )

        return AuthResponseDTO(
            access_token=token,
            token_type="bearer",
            user_id=created_user.id,
            tenant_id=created_tenant.id,
            role=created_user.role.value,
            full_name=created_user.full_name,
            email=created_user.email,
        )


class LoginUseCase:
    def __init__(
        self,
        tenant_repo: TenantRepository,
        user_repo: UserRepository,
    ):
        self.tenant_repo = tenant_repo
        self.user_repo = user_repo

    async def execute(self, email: str, password: str, tenant_slug: Optional[str] = None) -> AuthResponseDTO:
        # If tenant slug provided, verify tenant exists
        tenant_id = None
        if tenant_slug:
            tenant = await self.tenant_repo.get_by_slug(tenant_slug)
            if not tenant:
                raise ValueError("Tenant not found")
            tenant_id = tenant.id

        user = await self.user_repo.get_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")

        if tenant_id and user.tenant_id != tenant_id:
            raise ValueError("Invalid credentials for this organization")

        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("User account is inactive")

        token = create_access_token(
            subject=user.id,
            tenant_id=user.tenant_id,
            role=user.role.value,
            extra_claims={"full_name": user.full_name},
        )

        return AuthResponseDTO(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            tenant_id=user.tenant_id,
            role=user.role.value,
            full_name=user.full_name,
            email=user.email,
        )
