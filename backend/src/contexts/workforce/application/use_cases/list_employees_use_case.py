from typing import Optional
from src.contexts.workforce.domain.value_objects import EmployeeStatus
from src.contexts.workforce.domain.ports import EmployeeRepository
from src.contexts.workforce.application.dtos import PaginatedEmployeesDTO
from src.contexts.workforce.application.use_cases.mappers import to_employee_dto


class ListEmployeesUseCase:
    """Use Case responsible exclusively for paginating, filtering, and searching employees."""

    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        department: Optional[str] = None,
        status: Optional[EmployeeStatus] = None,
        search: Optional[str] = None,
    ) -> PaginatedEmployeesDTO:
        items, total = await self.employee_repo.list(
            skip=skip,
            limit=limit,
            department=department,
            status=status,
            search=search,
        )
        return PaginatedEmployeesDTO(
            items=[to_employee_dto(e) for e in items],
            total=total,
            skip=skip,
            limit=limit,
        )
