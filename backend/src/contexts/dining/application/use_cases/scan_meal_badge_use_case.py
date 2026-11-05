from datetime import datetime, timezone
from typing import Optional
from src.contexts.dining.domain.entities import MealRecord
from src.contexts.dining.domain.value_objects import MealType, MealStatus
from src.contexts.dining.domain.ports import MealRepository
from src.contexts.workforce.domain.ports import EmployeeRepository
from src.contexts.workforce.domain.value_objects import EmployeeStatus
from src.contexts.dining.application.dtos import ScanMealBadgeCommand, MealScanResultDTO
from src.shared.domain.event_bus import EventBus


class ScanMealBadgeUseCase:
    """
    Use Case: Processes dining hall QR badge scans.
    Enforces employee active status and prevents duplicate meal allowances in the same window.
    """

    def __init__(
        self,
        meal_repo: MealRepository,
        employee_repo: EmployeeRepository,
        event_bus: Optional[EventBus] = None,
    ):
        self.meal_repo = meal_repo
        self.employee_repo = employee_repo
        self.event_bus = event_bus

    async def execute(self, cmd: ScanMealBadgeCommand) -> MealScanResultDTO:
        # 1. Parse MealType
        try:
            meal_type = MealType(cmd.meal_type.lower())
        except ValueError:
            raise ValueError(f"Invalid meal type '{cmd.meal_type}'. Must be one of: {[m.value for m in MealType]}")

        # 2. Look up Employee by scanned badge code
        employee = await self.employee_repo.get_by_badge_code(cmd.badge_code)
        if not employee:
            raise ValueError(f"Credencial/QR '{cmd.badge_code}' no reconocida en el sistema.")

        # 3. Verify Employee status
        if employee.status != EmployeeStatus.ACTIVE:
            denied_record = MealRecord.record_denied(
                tenant_id=cmd.tenant_id,
                employee_id=employee.id,
                meal_type=meal_type,
                badge_code=cmd.badge_code,
                status=MealStatus.QUOTA_EXCEEDED,
                reason=f"Empleado en estado '{employee.status.value}'. Acceso denegado.",
            )
            saved_denied = await self.meal_repo.save(denied_record)
            if self.event_bus:
                await self.event_bus.publish(saved_denied.pull_domain_events())

            return MealScanResultDTO(
                id=saved_denied.id,
                status=saved_denied.status.value,
                approved=False,
                employee_id=employee.id,
                employee_name=employee.full_name,
                department=str(employee.department),
                meal_type=meal_type.value,
                badge_code=cmd.badge_code,
                message=f"Acceso denegado: el empleado se encuentra en estado '{employee.status.value}'.",
                consumed_at=saved_denied.consumed_at,
            )

        # 4. Enforce Single Meal Policy (prevent duplicate scans for same meal today)
        today = datetime.now(timezone.utc).date()
        already_consumed = await self.meal_repo.has_consumed_meal_on_date(
            employee_id=employee.id,
            meal_type=meal_type,
            target_date=today,
        )

        if already_consumed:
            denied_record = MealRecord.record_denied(
                tenant_id=cmd.tenant_id,
                employee_id=employee.id,
                meal_type=meal_type,
                badge_code=cmd.badge_code,
                status=MealStatus.DUPLICATE_REJECTED,
                reason=f"El empleado ya consumió su ración de {meal_type.value} hoy.",
            )
            saved_denied = await self.meal_repo.save(denied_record)
            if self.event_bus:
                await self.event_bus.publish(saved_denied.pull_domain_events())

            return MealScanResultDTO(
                id=saved_denied.id,
                status=saved_denied.status.value,
                approved=False,
                employee_id=employee.id,
                employee_name=employee.full_name,
                department=str(employee.department),
                meal_type=meal_type.value,
                badge_code=cmd.badge_code,
                message=f"Ración duplicada: ya se registró {meal_type.value} para hoy.",
                consumed_at=saved_denied.consumed_at,
            )

        # 5. Approve and Record Meal
        record = MealRecord.record_approved(
            tenant_id=cmd.tenant_id,
            employee_id=employee.id,
            meal_type=meal_type,
            badge_code=cmd.badge_code,
            notes=cmd.notes,
        )
        saved = await self.meal_repo.save(record)

        if self.event_bus:
            await self.event_bus.publish(saved.pull_domain_events())

        return MealScanResultDTO(
            id=saved.id,
            status=saved.status.value,
            approved=True,
            employee_id=employee.id,
            employee_name=employee.full_name,
            department=str(employee.department),
            meal_type=meal_type.value,
            badge_code=cmd.badge_code,
            message=f"¡Ración de {meal_type.value} aprobada exitosamente!",
            consumed_at=saved.consumed_at,
        )
