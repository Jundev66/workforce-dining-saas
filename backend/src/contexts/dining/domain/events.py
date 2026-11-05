from dataclasses import dataclass
from src.shared.domain.base import DomainEvent


@dataclass(frozen=True)
class MealRecordedDomainEvent(DomainEvent):
    meal_id: str = ""
    tenant_id: str = ""
    employee_id: str = ""
    meal_type: str = ""
    badge_code: str = ""
    status: str = ""


@dataclass(frozen=True)
class MealDeniedDomainEvent(DomainEvent):
    tenant_id: str = ""
    employee_id: str = ""
    meal_type: str = ""
    reason: str = ""
