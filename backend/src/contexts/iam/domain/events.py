from dataclasses import dataclass
from src.shared.domain.base import DomainEvent


@dataclass(frozen=True)
class TenantRegisteredDomainEvent(DomainEvent):
    tenant_id: str = ""
    slug: str = ""
    name: str = ""
    admin_email: str = ""
