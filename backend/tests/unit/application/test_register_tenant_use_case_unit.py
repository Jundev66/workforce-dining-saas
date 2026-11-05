import pytest
from unittest.mock import AsyncMock
from src.contexts.iam.domain.ports import TenantRepository, UserRepository
from src.contexts.iam.application.use_cases.register_tenant_use_case import RegisterTenantUseCase
from src.shared.domain.event_bus import InMemoryEventBus
from tests.mothers.tenant_mother import RegisterTenantCommandMother, TenantMother


@pytest.mark.asyncio
async def test_should_register_tenant_save_entities_and_publish_domain_events():
    # GIVEN
    tenant_repo = AsyncMock(spec=TenantRepository)
    user_repo = AsyncMock(spec=UserRepository)
    event_bus = InMemoryEventBus()

    tenant_repo.get_by_slug.return_value = None
    tenant_repo.create.side_effect = lambda t: t
    user_repo.create.side_effect = lambda u: u

    use_case = RegisterTenantUseCase(tenant_repo, user_repo, event_bus)
    cmd = RegisterTenantCommandMother.random()

    # WHEN
    dto = await use_case.execute(cmd)

    # THEN
    assert dto.access_token is not None
    assert dto.email == cmd.admin_email

    # AND repositories were called
    tenant_repo.get_by_slug.assert_awaited_once_with(cmd.tenant_slug)
    tenant_repo.create.assert_awaited_once()
    user_repo.create.assert_awaited_once()

    # AND domain events were published to the event bus
    assert len(event_bus.published_events) == 1
    assert event_bus.published_events[0].slug == cmd.tenant_slug


@pytest.mark.asyncio
async def test_should_fail_when_tenant_slug_already_exists():
    tenant_repo = AsyncMock(spec=TenantRepository)
    user_repo = AsyncMock(spec=UserRepository)

    existing = TenantMother.create(slug="already-taken")
    tenant_repo.get_by_slug.return_value = existing

    use_case = RegisterTenantUseCase(tenant_repo, user_repo)
    cmd = RegisterTenantCommandMother.create(tenant_slug="already-taken")

    with pytest.raises(ValueError, match="already exists"):
        await use_case.execute(cmd)

    tenant_repo.create.assert_not_awaited()
