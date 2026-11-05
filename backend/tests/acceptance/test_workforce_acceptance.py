import pytest
from typing import Dict, List, Optional, Tuple

from src.contexts.workforce.domain.entities import Employee
from src.contexts.workforce.domain.value_objects import (
    DocumentId,
    BadgeCode,
    Department,
    EmployeeStatus,
)
from src.contexts.workforce.domain.ports import EmployeeRepository
from src.contexts.workforce.application.use_cases import (
    CreateEmployeeUseCase,
    ListEmployeesUseCase,
    UpdateEmployeeUseCase,
)
from src.contexts.workforce.application.dtos import (
    CreateEmployeeCommand,
    UpdateEmployeeCommand,
)


class InMemoryEmployeeRepo(EmployeeRepository):
    def __init__(self):
        self._employees: Dict[str, Employee] = {}

    async def get_by_id(self, employee_id: str) -> Optional[Employee]:
        return self._employees.get(employee_id)

    async def get_by_document_id(self, document_id: str) -> Optional[Employee]:
        for e in self._employees.values():
            if str(e.document_id) == document_id.strip().upper():
                return e
        return None

    async def get_by_badge_code(self, badge_code: str) -> Optional[Employee]:
        for e in self._employees.values():
            if str(e.badge_code) == badge_code.strip().upper():
                return e
        return None

    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        department: Optional[str] = None,
        status: Optional[EmployeeStatus] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Employee], int]:
        items = list(self._employees.values())
        if department:
            items = [e for e in items if department.lower() in str(e.department).lower()]
        if status:
            items = [e for e in items if e.status == status]
        if search:
            s = search.lower()
            items = [
                e for e in items
                if s in e.first_name.lower() or s in e.last_name.lower() or s in str(e.document_id).lower()
            ]
        total = len(items)
        return items[skip : skip + limit], total

    async def create(self, employee: Employee) -> Employee:
        self._employees[employee.id] = employee
        return employee

    async def update(self, employee: Employee) -> Employee:
        self._employees[employee.id] = employee
        return employee

    async def delete(self, employee_id: str) -> bool:
        if employee_id in self._employees:
            del self._employees[employee_id]
            return True
        return False


@pytest.mark.asyncio
async def test_acceptance_employee_onboarding_and_event_publishing():
    """
    Feature: Employee Onboarding (ATDD)
    Scenario: Onboard a staff member and verify aggregate root domain events
    """
    # GIVEN
    repo = InMemoryEmployeeRepo()
    create_uc = CreateEmployeeUseCase(repo)
    update_uc = UpdateEmployeeUseCase(repo)

    # WHEN
    dto = await create_uc.execute(
        CreateEmployeeCommand(
            tenant_id="tenant-acme",
            first_name="Gonzalo",
            last_name="Montiel",
            document_id="DNI-44111222",
            department="Seguridad & Accesos",
            position="Supervisor",
            badge_code="SEC-990",
        )
    )

    # THEN
    assert dto.id is not None
    assert dto.badge_code == "SEC-990"
    assert dto.status == "active"

    # AND domain event was recorded on the aggregate root
    emp = await repo.get_by_id(dto.id)
    assert emp is not None
    events = emp.pull_domain_events()
    assert len(events) == 1
    assert events[0].document_id == "DNI-44111222"

    # WHEN: Employee status is changed to inactive
    updated_dto = await update_uc.execute(
        UpdateEmployeeCommand(
            employee_id=dto.id,
            status=EmployeeStatus.INACTIVE,
        )
    )

    # THEN
    assert updated_dto.status == "inactive"
    status_events = emp.pull_domain_events()
    assert len(status_events) == 1
    assert status_events[0].previous_status == "active"
    assert status_events[0].new_status == "inactive"


@pytest.mark.asyncio
async def test_acceptance_employee_document_value_object_invariants():
    """
    Feature: Document ID Invariants
    Scenario: Rejects short or invalid document numbers
    """
    repo = InMemoryEmployeeRepo()
    create_uc = CreateEmployeeUseCase(repo)

    with pytest.raises(ValueError, match="Document ID must be between 3 and 50 characters"):
        await create_uc.execute(
            CreateEmployeeCommand(
                tenant_id="tenant-acme",
                first_name="Test",
                last_name="User",
                document_id="A",  # Invalid: too short
            )
        )
