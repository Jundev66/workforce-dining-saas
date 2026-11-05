from src.contexts.workforce.domain.ports import EmployeeRepository
from src.contexts.workforce.application.dtos import UpdateEmployeeCommand, EmployeeDTO
from src.contexts.workforce.application.use_cases.mappers import to_employee_dto


class UpdateEmployeeUseCase:
    """Use Case responsible exclusively for updating employee profile attributes and status."""

    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo

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
        return to_employee_dto(saved)
