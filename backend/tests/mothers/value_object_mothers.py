import uuid
from src.contexts.iam.domain.value_objects import TenantSlug, EmailAddress
from src.contexts.workforce.domain.value_objects import DocumentId, BadgeCode, Department


class TenantSlugMother:
    @staticmethod
    def create(value: str = "acme-corp") -> TenantSlug:
        return TenantSlug(value)

    @staticmethod
    def random() -> TenantSlug:
        return TenantSlug(f"org-{uuid.uuid4().hex[:6]}")


class EmailAddressMother:
    @staticmethod
    def create(value: str = "admin@example.com") -> EmailAddress:
        return EmailAddress(value)

    @staticmethod
    def random() -> EmailAddress:
        return EmailAddress(f"user_{uuid.uuid4().hex[:6]}@domain.com")


class DocumentIdMother:
    @staticmethod
    def create(value: str = "DOC-123456") -> DocumentId:
        return DocumentId(value)

    @staticmethod
    def random() -> DocumentId:
        return DocumentId(f"DNI-{uuid.uuid4().hex[:8].upper()}")


class BadgeCodeMother:
    @staticmethod
    def create(value: str = "BADGE-999") -> BadgeCode:
        return BadgeCode(value)

    @staticmethod
    def random() -> BadgeCode:
        return BadgeCode(f"QR-{uuid.uuid4().hex[:8].upper()}")


class DepartmentMother:
    @staticmethod
    def create(value: str = "Operations") -> Department:
        return Department(value)
