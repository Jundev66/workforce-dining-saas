from datetime import datetime, timezone
from typing import Optional
import uuid

from src.shared.domain.base import AggregateRoot
from src.contexts.iam.domain.value_objects import TenantSlug, EmailAddress, UserRole
from src.contexts.iam.domain.events import TenantRegisteredDomainEvent


class Tenant(AggregateRoot):
    def __init__(
        self,
        id: str,
        name: str,
        slug: TenantSlug,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__()
        self.id = id
        self.name = name.strip()
        self.slug = slug
        self.is_active = is_active
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    @classmethod
    def create(cls, name: str, slug: str, admin_email: Optional[str] = None) -> "Tenant":
        if not name or len(name.strip()) < 2:
            raise ValueError("Tenant name must have at least 2 characters.")
        tenant_id = str(uuid.uuid4())
        tenant_slug = TenantSlug(slug)
        tenant = cls(
            id=tenant_id,
            name=name,
            slug=tenant_slug,
            is_active=True,
        )
        tenant.record_event(
            TenantRegisteredDomainEvent(
                tenant_id=tenant_id,
                slug=str(tenant_slug),
                name=tenant.name,
                admin_email=admin_email or "",
            )
        )
        return tenant


class User(AggregateRoot):
    def __init__(
        self,
        id: str,
        tenant_id: str,
        email: EmailAddress,
        hashed_password: str,
        full_name: str,
        role: UserRole = UserRole.ADMIN,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__()
        self.id = id
        self.tenant_id = tenant_id
        self.email = email
        self.hashed_password = hashed_password
        self.full_name = full_name.strip()
        self.role = role
        self.is_active = is_active
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    @classmethod
    def create(
        cls,
        tenant_id: str,
        email: str,
        hashed_password: str,
        full_name: str,
        role: UserRole = UserRole.ADMIN,
    ) -> "User":
        if not full_name or len(full_name.strip()) < 2:
            raise ValueError("Full name must have at least 2 characters.")
        return cls(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            email=EmailAddress(email),
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            is_active=True,
        )
