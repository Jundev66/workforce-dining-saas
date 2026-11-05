import pytest
from unittest.mock import AsyncMock
from src.contexts.workforce.domain.ports import EmployeeRepository
from src.contexts.workforce.application.use_cases.create_employee_use_case import CreateEmployeeUseCase
from src.shared.domain.event_bus import InMemoryEventBus
from tests.mothers.employee_mother import CreateEmployeeCommandMother, EmployeeMother


@pytest.mark.asyncio
async def test_should_create_employee_save_to_repo_and_publish_event():
    # GIVEN
    repo = AsyncMock(spec=EmployeeRepository)
    repo.get_by_document_id.return_value = None
    repo.get_by_badge_code.return_value = None
    repo.create.side_effect = lambda emp: emp

    event_bus = InMemoryEventBus()
    use_case = CreateEmployeeUseCase(repo, event_bus)
    cmd = CreateEmployeeCommandMother.random()

    # WHEN
    dto = await use_case.execute(cmd)

    # THEN
    assert dto.document_id == cmd.document_id.upper()
    assert dto.status == "active"

    # AND repo was called
    repo.get_by_document_id.assert_awaited_once_with(cmd.document_id)
    repo.create.assert_awaited_once()

    # AND domain event was published to the event bus
    assert len(event_bus.published_events) == 1
    assert event_bus.published_events[0].document_id == cmd.document_id.upper()


@pytest.mark.asyncio
async def test_should_fail_when_employee_document_already_exists():
    repo = AsyncMock(spec=EmployeeRepository)
    existing = EmployeeMother.create(document_id="DOC-DUPLICATE")
    repo.get_by_document_id.return_value = existing

    use_case = CreateEmployeeUseCase(repo)
    cmd = CreateEmployeeCommandMother.create(document_id="DOC-DUPLICATE")

    with pytest.raises(ValueError, match="already exists"):
        await use_case.execute(cmd)

    repo.create.assert_not_awaited()
