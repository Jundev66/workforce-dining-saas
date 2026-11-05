import pytest
from unittest.mock import AsyncMock
from src.contexts.workforce.domain.ports import EmployeeRepository
from src.contexts.workforce.domain.value_objects import EmployeeStatus
from src.contexts.workforce.application.use_cases.update_employee_use_case import UpdateEmployeeUseCase
from src.shared.domain.event_bus import InMemoryEventBus
from tests.mothers.employee_mother import EmployeeMother, UpdateEmployeeCommandMother


@pytest.mark.asyncio
async def test_should_update_employee_status_and_publish_status_changed_event():
    # GIVEN
    repo = AsyncMock(spec=EmployeeRepository)
    employee = EmployeeMother.create()
    employee.pull_domain_events()  # Clear initial create event
    repo.get_by_id.return_value = employee
    repo.update.side_effect = lambda emp: emp

    event_bus = InMemoryEventBus()
    use_case = UpdateEmployeeUseCase(repo, event_bus)
    cmd = UpdateEmployeeCommandMother.create(
        employee_id=employee.id,
        status=EmployeeStatus.INACTIVE,
    )

    # WHEN
    dto = await use_case.execute(cmd)

    # THEN
    assert dto.status == "inactive"
    repo.get_by_id.assert_awaited_once_with(employee.id)
    repo.update.assert_awaited_once()

    # AND status change event was published
    assert len(event_bus.published_events) == 1
    assert event_bus.published_events[0].new_status == "inactive"


@pytest.mark.asyncio
async def test_should_fail_when_employee_to_update_does_not_exist():
    repo = AsyncMock(spec=EmployeeRepository)
    repo.get_by_id.return_value = None

    use_case = UpdateEmployeeUseCase(repo)
    cmd = UpdateEmployeeCommandMother.create(employee_id="non-existent")

    with pytest.raises(ValueError, match="not found"):
        await use_case.execute(cmd)
