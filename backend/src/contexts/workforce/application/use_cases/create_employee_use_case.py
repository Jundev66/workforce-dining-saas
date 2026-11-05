from src.contexts.workforce.domain.entities import Employee
from src.contexts.workforce.domain.ports import EmployeeRepository
from src.contexts.workforce.application.dtos import CreateEmployeeCommand, EmployeeDTO
from src.contexts.workforce.application.use_cases.mappers import to_employee_dto


class CreateEmployeeUseCase:
    """Use Case responsible exclusively for registering a new employee in the workforce."""

    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo

    async def execute(self, cmd: CreateEmployeeCommand) -> EmployeeDTO:
        existing_doc = await self.employee_repo.get_by_document_id(cmd.document_id)
        if existing_doc:
            raise ValueError(f"Employee with document ID '{cmd.document_id}' already exists in this organization.")

        if cmd.badge_code:
            existing_badge = await self.employee_repo.get_by_badge_code(cmd.badge_code)
            if existing_badge:
                raise ValueError(f"Badge code '{cmd.badge_code}' is already assigned to another employee.")

        employee = Employee.create(
            tenant_id=cmd.tenant_id,
            first_name=cmd.first_name,
            last_name=cmd.last_name,
            document_id=cmd.document_id,
            department=cmd.department,
            position=cmd.position,
            email=cmd.email,
            phone=cmd.phone,
            badge_code=cmd.badge_code,
        )

        saved = await self.employee_repo.create(employee)
        return to_employee_dto(saved)
