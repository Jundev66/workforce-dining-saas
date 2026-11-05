import pytest
from src.contexts.iam.domain.entities import Tenant
from tests.mothers.tenant_mother import TenantMother


def test_should_create_tenant_and_record_domain_event():
    # GIVEN / WHEN
    tenant = TenantMother.random()

    # THEN
    assert tenant.id is not None
    assert tenant.is_active is True

    # AND domain event was recorded
    events = tenant.pull_domain_events()
    assert len(events) == 1
    assert events[0].tenant_id == tenant.id

    # AND pull clears internal buffer
    assert len(tenant.pull_domain_events()) == 0


def test_should_throw_error_when_tenant_name_is_invalid():
    with pytest.raises(ValueError, match="Tenant name must have at least 2 characters"):
        Tenant.create(name="A", slug="valid-slug")
