import pytest
from src.contexts.iam.domain.value_objects import TenantSlug, EmailAddress
from src.contexts.workforce.domain.value_objects import DocumentId, BadgeCode, Department


def test_tenant_slug_invariants():
    # Valid
    slug = TenantSlug("acme-industries")
    assert str(slug) == "acme-industries"

    # Invalid uppercase or spaces
    with pytest.raises(ValueError, match="Invalid tenant slug"):
        TenantSlug("Acme Industries")

    # Invalid characters
    with pytest.raises(ValueError, match="Invalid tenant slug"):
        TenantSlug("acme@corp")


def test_email_address_invariants():
    # Valid
    email = EmailAddress("admin@company.com")
    assert str(email) == "admin@company.com"

    # Invalid
    with pytest.raises(ValueError, match="Invalid email address"):
        EmailAddress("not-an-email")


def test_document_id_invariants():
    doc = DocumentId("dni-12345")
    assert str(doc) == "DNI-12345"

    with pytest.raises(ValueError, match="Document ID must be between 3 and 50 characters"):
        DocumentId("1")


def test_badge_code_invariants():
    badge = BadgeCode("badge-xyz")
    assert str(badge) == "BADGE-XYZ"

    with pytest.raises(ValueError, match="Badge code must be between 3 and 100 characters"):
        BadgeCode("B")
