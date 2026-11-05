from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, Query, status

from src.contexts.workforce.domain.value_objects import EmployeeStatus
from src.contexts.workforce.application.use_cases.list_employees_use_case import ListEmployeesUseCase
from src.contexts.workforce.application.dtos import PaginatedEmployeesDTO
from src.contexts.workforce.infrastructure.persistence.repositories import SQLAlchemyEmployeeRepository
from src.contexts.workforce.presentation.controllers.common import (
    get_employee_repo,
    get_current_user,
)


class ListEmployeesController:
    """Single-Action Controller: Handles paginated query, search, and department/status filtering."""

    @staticmethod
    async def handle(
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        department: Optional[str] = Query(None),
        status_filter: Optional[str] = Query(None, alias="status"),
        search: Optional[str] = Query(None),
        current_user: Dict[str, Any] = Depends(get_current_user),
        repo: SQLAlchemyEmployeeRepository = Depends(get_employee_repo),
    ) -> PaginatedEmployeesDTO:
        status_enum = None
        if status_filter:
            try:
                status_enum = EmployeeStatus(status_filter.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status. Must be one of {[s.value for s in EmployeeStatus]}",
                )

        use_case = ListEmployeesUseCase(repo)
        return await use_case.execute(
            skip=skip,
            limit=limit,
            department=department,
            status=status_enum,
            search=search,
        )
