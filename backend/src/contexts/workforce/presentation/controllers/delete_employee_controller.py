from typing import Dict, Any
from fastapi import Depends, HTTPException, status

from src.contexts.workforce.application.use_cases.delete_employee_use_case import DeleteEmployeeUseCase
from src.contexts.workforce.infrastructure.persistence.repositories import SQLAlchemyEmployeeRepository
from src.contexts.workforce.presentation.controllers.common import (
    get_employee_repo,
    get_current_user,
)


class DeleteEmployeeController:
    """Single-Action Controller: Handles employee deletion/offboarding."""

    @staticmethod
    async def handle(
        employee_id: str,
        current_user: Dict[str, Any] = Depends(get_current_user),
        repo: SQLAlchemyEmployeeRepository = Depends(get_employee_repo),
    ) -> None:
        use_case = DeleteEmployeeUseCase(repo)
        try:
            await use_case.execute(employee_id)
            return None
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
