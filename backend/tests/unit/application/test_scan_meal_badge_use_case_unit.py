import pytest
from unittest.mock import AsyncMock
from src.contexts.dining.domain.ports import MealRepository
from src.contexts.workforce.domain.ports import EmployeeRepository
from src.contexts.workforce.domain.value_objects import EmployeeStatus
from src.contexts.dining.application.use_cases.scan_meal_badge_use_case import ScanMealBadgeUseCase
from src.shared.domain.event_bus import InMemoryEventBus
from tests.mothers.employee_mother import EmployeeMother
from tests.mothers.meal_mother import ScanMealBadgeCommandMother


@pytest.mark.asyncio
async def test_should_approve_valid_meal_scan_and_publish_event():
    # GIVEN
    meal_repo = AsyncMock(spec=MealRepository)
    employee_repo = AsyncMock(spec=EmployeeRepository)
    event_bus = InMemoryEventBus()

    employee = EmployeeMother.create(badge_code="QR-TEST")
    employee_repo.get_by_badge_code.return_value = employee
    meal_repo.has_consumed_meal_on_date.return_value = False
    meal_repo.save.side_effect = lambda m: m

    use_case = ScanMealBadgeUseCase(meal_repo, employee_repo, event_bus)
    cmd = ScanMealBadgeCommandMother.create(badge_code="QR-TEST", meal_type="lunch")

    # WHEN
    result = await use_case.execute(cmd)

    # THEN
    assert result.approved is True
    assert result.status == "approved"
    assert result.employee_name == employee.full_name

    meal_repo.save.assert_awaited_once()
    assert len(event_bus.published_events) == 1
    assert event_bus.published_events[0].status == "approved"


@pytest.mark.asyncio
async def test_should_deny_duplicate_meal_scan_on_same_day():
    # GIVEN
    meal_repo = AsyncMock(spec=MealRepository)
    employee_repo = AsyncMock(spec=EmployeeRepository)
    event_bus = InMemoryEventBus()

    employee = EmployeeMother.create(badge_code="QR-DUPE")
    employee_repo.get_by_badge_code.return_value = employee
    meal_repo.has_consumed_meal_on_date.return_value = True  # Already consumed today!
    meal_repo.save.side_effect = lambda m: m

    use_case = ScanMealBadgeUseCase(meal_repo, employee_repo, event_bus)
    cmd = ScanMealBadgeCommandMother.create(badge_code="QR-DUPE", meal_type="lunch")

    # WHEN
    result = await use_case.execute(cmd)

    # THEN
    assert result.approved is False
    assert result.status == "duplicate_rejected"
    assert "ya se registró lunch" in result.message

    meal_repo.save.assert_awaited_once()
    assert len(event_bus.published_events) == 1
    assert "ya consumió su ración" in event_bus.published_events[0].reason.lower()


@pytest.mark.asyncio
async def test_should_deny_meal_for_inactive_employee():
    meal_repo = AsyncMock(spec=MealRepository)
    employee_repo = AsyncMock(spec=EmployeeRepository)

    employee = EmployeeMother.create(badge_code="QR-INACTIVE")
    employee.change_status(EmployeeStatus.INACTIVE)
    employee_repo.get_by_badge_code.return_value = employee
    meal_repo.save.side_effect = lambda m: m

    use_case = ScanMealBadgeUseCase(meal_repo, employee_repo)
    cmd = ScanMealBadgeCommandMother.create(badge_code="QR-INACTIVE")

    result = await use_case.execute(cmd)
    assert result.approved is False
    assert result.status == "quota_exceeded"
