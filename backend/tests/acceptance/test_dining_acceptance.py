import pytest
from datetime import date
from typing import Dict, List
from src.contexts.dining.domain.entities import MealRecord
from src.contexts.dining.domain.value_objects import MealType
from src.contexts.dining.domain.ports import MealRepository
from src.contexts.dining.application.use_cases.scan_meal_badge_use_case import ScanMealBadgeUseCase
from src.contexts.dining.application.dtos import ScanMealBadgeCommand
from tests.acceptance.test_workforce_acceptance import InMemoryEmployeeRepo
from tests.mothers.employee_mother import EmployeeMother


class InMemoryMealRepo(MealRepository):
    def __init__(self):
        self._meals: List[MealRecord] = []

    async def save(self, meal: MealRecord) -> MealRecord:
        self._meals.append(meal)
        return meal

    async def has_consumed_meal_on_date(
        self,
        employee_id: str,
        meal_type: MealType,
        target_date: date,
    ) -> bool:
        for m in self._meals:
            if (
                m.employee_id == employee_id
                and m.meal_type == meal_type
                and m.status.value == "approved"
                and m.consumed_at.date() == target_date
            ):
                return True
        return False

    async def get_daily_metrics(self, tenant_id: str, target_date: date) -> Dict[str, int]:
        metrics = {"breakfast": 0, "lunch": 0, "dinner": 0, "rejected": 0}
        for m in self._meals:
            if m.tenant_id == tenant_id and m.consumed_at.date() == target_date:
                if m.status.value == "approved":
                    metrics[m.meal_type.value] = metrics.get(m.meal_type.value, 0) + 1
                else:
                    metrics["rejected"] += 1
        return metrics

    async def list_recent(self, skip: int = 0, limit: int = 50) -> List[MealRecord]:
        return self._meals[skip : skip + limit]


@pytest.mark.asyncio
async def test_acceptance_dining_badge_scanning_and_duplicate_prevention():
    """
    Feature: Dining Hall Meal Scanning (ATDD)
    Scenario: Active employee scans badge for lunch; second scan is rejected.
    """
    # GIVEN
    meal_repo = InMemoryMealRepo()
    emp_repo = InMemoryEmployeeRepo()

    employee = EmployeeMother.create(
        tenant_id="tenant-diners",
        badge_code="QR-DINER-01",
    )
    await emp_repo.create(employee)

    use_case = ScanMealBadgeUseCase(meal_repo, emp_repo)

    # WHEN: First scan for lunch
    first_scan = await use_case.execute(
        ScanMealBadgeCommand(
            tenant_id="tenant-diners",
            badge_code="QR-DINER-01",
            meal_type="lunch",
        )
    )

    # THEN: Approved
    assert first_scan.approved is True
    assert first_scan.status == "approved"

    # WHEN: Scanning again for lunch on same day
    second_scan = await use_case.execute(
        ScanMealBadgeCommand(
            tenant_id="tenant-diners",
            badge_code="QR-DINER-01",
            meal_type="lunch",
        )
    )

    # THEN: Denied as duplicate
    assert second_scan.approved is False
    assert second_scan.status == "duplicate_rejected"
