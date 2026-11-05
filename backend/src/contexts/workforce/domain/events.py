from dataclasses import dataclass
from src.shared.domain.base import DomainEvent


@dataclass(frozen=True)
class EmployeeOnboardedDomainEvent(DomainEvent):
    employee_id: str = ""
    tenant_id: str = ""
    document_id: str = ""
    badge_code: str = ""


@dataclass(frozen=True)
class EmployeeStatusChangedDomainEvent(DomainEvent):
    employee_id: str = ""
    tenant_id: str = ""
    previous_status: str = ""
    new_status: str = ""
