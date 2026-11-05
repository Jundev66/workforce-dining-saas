import pytest
from typing import Dict, Optional
from src.contexts.iam.domain.entities import Tenant, User
from src.contexts.iam.domain.value_objects import TenantSlug, EmailAddress
from src.contexts.iam.domain.ports import TenantRepository, UserRepository
from src.contexts.iam.application.use_cases import RegisterTenantUseCase, LoginUseCase
from src.contexts.iam.application.dtos import RegisterTenantCommand, LoginCommand


class InMemoryTenantRepo(TenantRepository):
    def __init__(self):
        self._tenants: Dict[str, Tenant] = {}

    async def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        return self._tenants.get(tenant_id)

    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        for t in self._tenants.values():
            if str(t.slug) == slug.lower().strip():
                return t
        return None

    async def create(self, tenant: Tenant) -> Tenant:
        self._tenants[tenant.id] = tenant
        return tenant


class InMemoryUserRepo(UserRepository):
    def __init__(self):
        self._users: Dict[str, User] = {}

    async def get_by_id(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        for u in self._users.values():
            if str(u.email) == email.lower().strip():
                return u
        return None

    async def create(self, user: User) -> User:
        self._users[user.id] = user
        return user


@pytest.mark.asyncio
async def test_acceptance_tenant_onboarding_and_authentication():
    """
    Feature: SaaS Multi-Tenant Onboarding (ATDD)
    Scenario: Successfully register a new tenant and login with admin credentials
    """
    # GIVEN
    tenant_repo = InMemoryTenantRepo()
    user_repo = InMemoryUserRepo()
    register_uc = RegisterTenantUseCase(tenant_repo, user_repo)
    login_uc = LoginUseCase(tenant_repo, user_repo)

    # WHEN
    reg_cmd = RegisterTenantCommand(
        tenant_name="Logistica Global S.A.",
        tenant_slug="logistica-global",
        admin_email="diego@logistica.com",
        admin_password="SuperPassword123!",
        admin_full_name="Diego Maradona",
    )
    auth_dto = await register_uc.execute(reg_cmd)

    # THEN
    assert auth_dto.access_token is not None
    assert auth_dto.role == "admin"
    assert auth_dto.email == "diego@logistica.com"

    # AND domain events were recorded on the aggregate root
    created_tenant = await tenant_repo.get_by_id(auth_dto.tenant_id)
    assert created_tenant is not None
    events = created_tenant.pull_domain_events()
    assert len(events) == 1
    assert events[0].slug == "logistica-global"

    # WHEN: Logging in with valid credentials
    login_dto = await login_uc.execute(
        LoginCommand(
            email="diego@logistica.com",
            password="SuperPassword123!",
            tenant_slug="logistica-global",
        )
    )

    # THEN
    assert login_dto.access_token is not None
    assert login_dto.user_id == auth_dto.user_id


@pytest.mark.asyncio
async def test_acceptance_tenant_slug_value_object_invariants():
    """
    Feature: Tenant Domain Invariants
    Scenario: System rejects invalid tenant slug formats
    """
    tenant_repo = InMemoryTenantRepo()
    user_repo = InMemoryUserRepo()
    register_uc = RegisterTenantUseCase(tenant_repo, user_repo)

    with pytest.raises(ValueError, match="Invalid tenant slug"):
        await register_uc.execute(
            RegisterTenantCommand(
                tenant_name="Empresa Mala",
                tenant_slug="invalid slug with spaces!",
                admin_email="test@empresa.com",
                admin_password="Password123!",
                admin_full_name="Tester",
            )
        )
