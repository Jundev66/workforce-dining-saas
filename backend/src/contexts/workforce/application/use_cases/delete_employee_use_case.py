from src.contexts.workforce.domain.ports import EmployeeRepository


class DeleteEmployeeUseCase:
    """Use Case responsible exclusively for deleting/offboarding an employee."""

    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo

    async def execute(self, employee_id: str) -> bool:
        success = await self.employee_repo.delete(employee_id)
        if not success:
            raise ValueError(f"Employee with ID '{employee_id}' not found.")
        return True
