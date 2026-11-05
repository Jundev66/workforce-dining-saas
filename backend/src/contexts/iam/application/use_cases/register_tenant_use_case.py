from typing import Optional
from src.contexts.iam.domain.entities import Tenant, User, UserRole
from src.contexts.iam.domain.ports import TenantRepository, UserRepository
from src.contexts.iam.application.dtos import RegisterTenantCommand, AuthResponseDTO
from src.shared.domain.event_bus import EventBus
from src.shared.infrastructure.security import hash_password, create_access_token


class RegisterTenantUseCase:
    """Use Case responsible exclusively for tenant registration and initial admin user creation."""

    def __init__(
        self,
        tenant_repo: TenantRepository,
        user_repo: UserRepository,
        event_bus: Optional[EventBus] = None,
    ):
        self.tenant_repo = tenant_repo
        self.user_repo = user_repo
        self.event_bus = event_bus

    async def execute(self, cmd: RegisterTenantCommand) -> AuthResponseDTO:
        existing_tenant = await self.tenant_repo.get_by_slug(cmd.tenant_slug)
        if existing_tenant:
            raise ValueError(f"A tenant with slug '{cmd.tenant_slug}' already exists")

        # 1. Create Tenant Aggregate Root (records TenantRegisteredDomainEvent)
        tenant = Tenant.create(
            name=cmd.tenant_name,
            slug=cmd.tenant_slug,
            admin_email=cmd.admin_email,
        )
        created_tenant = await self.tenant_repo.create(tenant)

        # 2. Create Admin User Aggregate Root
        hashed_pwd = hash_password(cmd.admin_password)
        admin_user = User.create(
            tenant_id=created_tenant.id,
            email=cmd.admin_email,
            hashed_password=hashed_pwd,
            full_name=cmd.admin_full_name,
            role=UserRole.ADMIN,
        )
        created_user = await self.user_repo.create(admin_user)

        # 3. Publish Domain Events via EventBus
        if self.event_bus:
            events = tenant.pull_domain_events() + admin_user.pull_domain_events()
            if events:
                await self.event_bus.publish(events)

        # 4. Issue JWT Token
        token = create_access_token(
            subject=created_user.id,
            tenant_id=created_tenant.id,
            role=created_user.role.value,
            extra_claims={
                "tenant_slug": str(created_tenant.slug),
                "full_name": created_user.full_name,
            },
        )

        return AuthResponseDTO(
            access_token=token,
            token_type="bearer",
            user_id=created_user.id,
            tenant_id=created_tenant.id,
            role=created_user.role.value,
            full_name=created_user.full_name,
            email=str(created_user.email),
        )
