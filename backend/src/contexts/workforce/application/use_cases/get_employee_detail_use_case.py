from src.contexts.workforce.domain.ports import EmployeeRepository
from src.contexts.workforce.application.dtos import EmployeeDTO
from src.contexts.workforce.application.use_cases.mappers import to_employee_dto


class GetEmployeeDetailUseCase:
    """Use Case responsible exclusively for fetching a single employee's full details."""

    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo

    async def execute(self, employee_id: str) -> EmployeeDTO:
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee with ID '{employee_id}' not found.")
        return to_employee_dto(employee)
