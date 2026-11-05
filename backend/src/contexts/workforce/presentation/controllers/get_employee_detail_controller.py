from typing import Dict, Any
from fastapi import Depends, HTTPException, status

from src.contexts.workforce.application.use_cases.get_employee_detail_use_case import GetEmployeeDetailUseCase
from src.contexts.workforce.application.dtos import EmployeeDTO
from src.contexts.workforce.infrastructure.persistence.repositories import SQLAlchemyEmployeeRepository
from src.contexts.workforce.presentation.controllers.common import (
    get_employee_repo,
    get_current_user,
)


class GetEmployeeDetailController:
    """Single-Action Controller: Retrieves a single employee's comprehensive profile."""

    @staticmethod
    async def handle(
        employee_id: str,
        current_user: Dict[str, Any] = Depends(get_current_user),
        repo: SQLAlchemyEmployeeRepository = Depends(get_employee_repo),
    ) -> EmployeeDTO:
        use_case = GetEmployeeDetailUseCase(repo)
        try:
            return await use_case.execute(employee_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
