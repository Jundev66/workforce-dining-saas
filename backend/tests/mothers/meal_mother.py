import uuid
from src.contexts.dining.domain.entities import MealRecord
from src.contexts.dining.domain.value_objects import MealType
from src.contexts.dining.application.dtos import ScanMealBadgeCommand


class MealRecordMother:
    @staticmethod
    def create_approved(
        tenant_id: str = "tenant-001",
        employee_id: str = "emp-001",
        meal_type: MealType = MealType.LUNCH,
        badge_code: str = "QR-100",
    ) -> MealRecord:
        return MealRecord.record_approved(
            tenant_id=tenant_id,
            employee_id=employee_id,
            meal_type=meal_type,
            badge_code=badge_code,
        )


class ScanMealBadgeCommandMother:
    @staticmethod
    def create(
        tenant_id: str = "tenant-001",
        badge_code: str = "QR-100",
        meal_type: str = "lunch",
    ) -> ScanMealBadgeCommand:
        return ScanMealBadgeCommand(
            tenant_id=tenant_id,
            badge_code=badge_code,
            meal_type=meal_type,
        )
