from datetime import datetime, timezone
from typing import Optional
import uuid

from src.shared.domain.base import AggregateRoot
from src.contexts.dining.domain.value_objects import MealType, MealStatus
from src.contexts.dining.domain.events import (
    MealRecordedDomainEvent,
    MealDeniedDomainEvent,
)


class MealRecord(AggregateRoot):
    def __init__(
        self,
        id: str,
        tenant_id: str,
        employee_id: str,
        meal_type: MealType,
        badge_code: str,
        status: MealStatus = MealStatus.APPROVED,
        notes: Optional[str] = None,
        consumed_at: Optional[datetime] = None,
    ):
        super().__init__()
        self.id = id
        self.tenant_id = tenant_id
        self.employee_id = employee_id
        self.meal_type = meal_type
        self.badge_code = badge_code.strip().upper()
        self.status = status
        self.notes = notes
        self.consumed_at = consumed_at or datetime.now(timezone.utc)

    @classmethod
    def record_approved(
        cls,
        tenant_id: str,
        employee_id: str,
        meal_type: MealType,
        badge_code: str,
        notes: Optional[str] = None,
    ) -> "MealRecord":
        record_id = str(uuid.uuid4())
        record = cls(
            id=record_id,
            tenant_id=tenant_id,
            employee_id=employee_id,
            meal_type=meal_type,
            badge_code=badge_code,
            status=MealStatus.APPROVED,
            notes=notes,
        )
        record.record_event(
            MealRecordedDomainEvent(
                meal_id=record_id,
                tenant_id=tenant_id,
                employee_id=employee_id,
                meal_type=meal_type.value,
                badge_code=record.badge_code,
                status=MealStatus.APPROVED.value,
            )
        )
        return record

    @classmethod
    def record_denied(
        cls,
        tenant_id: str,
        employee_id: str,
        meal_type: MealType,
        badge_code: str,
        status: MealStatus,
        reason: str,
    ) -> "MealRecord":
        record_id = str(uuid.uuid4())
        record = cls(
            id=record_id,
            tenant_id=tenant_id,
            employee_id=employee_id,
            meal_type=meal_type,
            badge_code=badge_code,
            status=status,
            notes=reason,
        )
        record.record_event(
            MealDeniedDomainEvent(
                tenant_id=tenant_id,
                employee_id=employee_id,
                meal_type=meal_type.value,
                reason=reason,
            )
        )
        return record
