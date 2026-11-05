import pytest
from src.contexts.workforce.domain.entities import Employee
from src.contexts.workforce.domain.value_objects import EmployeeStatus
from tests.mothers.employee_mother import EmployeeMother


def test_should_create_employee_and_record_onboarded_domain_event():
    # GIVEN / WHEN
    employee = EmployeeMother.create()

    # THEN
    assert employee.id is not None
    assert employee.status == EmployeeStatus.ACTIVE
    assert employee.full_name == "Julian Alvarez"

    # AND domain event was recorded
    events = employee.pull_domain_events()
    assert len(events) == 1
    assert events[0].employee_id == employee.id
    assert events[0].document_id == "DOC-998877"


def test_should_record_event_when_employee_status_changes():
    # GIVEN
    employee = EmployeeMother.create()
    employee.pull_domain_events()  # Clear initial onboarded event

    # WHEN
    employee.change_status(EmployeeStatus.ON_LEAVE)

    # THEN
    assert employee.status == EmployeeStatus.ON_LEAVE
    events = employee.pull_domain_events()
    assert len(events) == 1
    assert events[0].previous_status == "active"
    assert events[0].new_status == "on_leave"


def test_should_throw_error_when_employee_first_name_is_empty():
    with pytest.raises(ValueError, match="First name cannot be empty"):
        Employee.create(
            tenant_id="tenant-1",
            first_name="",
            last_name="Perez",
            document_id="DOC-123",
        )
