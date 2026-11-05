from typing import Optional
from src.contexts.workforce.domain.ports import EmployeeRepository
from src.contexts.workforce.application.dtos import UpdateEmployeeCommand, EmployeeDTO
from src.contexts.workforce.application.use_cases.mappers import to_employee_dto
from src.shared.domain.event_bus import EventBus


class UpdateEmployeeUseCase:
    """Use Case responsible exclusively for updating employee profile attributes and status."""

    def __init__(
        self,
        employee_repo: EmployeeRepository,
        event_bus: Optional[EventBus] = None,
    ):
        self.employee_repo = employee_repo
        self.event_bus = event_bus

    async def execute(self, cmd: UpdateEmployeeCommand) -> EmployeeDTO:
        employee = await self.employee_repo.get_by_id(cmd.employee_id)
        if not employee:
            raise ValueError(f"Employee with ID '{cmd.employee_id}' not found.")

        employee.update_profile(
            first_name=cmd.first_name,
            last_name=cmd.last_name,
            department=cmd.department,
            position=cmd.position,
            email=cmd.email,
            phone=cmd.phone,
        )

        if cmd.status is not None:
            employee.change_status(cmd.status)

        saved = await self.employee_repo.update(employee)

        # Publish Domain Events (such as EmployeeStatusChangedDomainEvent)
        if self.event_bus:
            events = employee.pull_domain_events()
            if events:
                await self.event_bus.publish(events)

        return to_employee_dto(saved)
