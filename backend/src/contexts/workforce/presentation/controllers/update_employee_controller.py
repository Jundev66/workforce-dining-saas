from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from src.contexts.workforce.domain.value_objects import EmployeeStatus
from src.contexts.workforce.application.use_cases.update_employee_use_case import UpdateEmployeeUseCase
from src.contexts.workforce.application.dtos import UpdateEmployeeCommand, EmployeeDTO
from src.contexts.workforce.infrastructure.persistence.repositories import SQLAlchemyEmployeeRepository
from src.contexts.workforce.presentation.controllers.common import (
    get_employee_repo,
    get_current_user,
)


class EmployeeUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    department: Optional[str] = Field(default=None, max_length=100)
    position: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    status: Optional[str] = None


class UpdateEmployeeController:
    """Single-Action Controller: Handles profile modifications and status changes."""

    @staticmethod
    async def handle(
        employee_id: str,
        data: EmployeeUpdateRequest,
        current_user: Dict[str, Any] = Depends(get_current_user),
        repo: SQLAlchemyEmployeeRepository = Depends(get_employee_repo),
    ) -> EmployeeDTO:
        status_enum = None
        if data.status:
            try:
                status_enum = EmployeeStatus(data.status.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status. Must be one of {[s.value for s in EmployeeStatus]}",
                )

        use_case = UpdateEmployeeUseCase(repo)
        try:
            return await use_case.execute(
                UpdateEmployeeCommand(
                    employee_id=employee_id,
                    first_name=data.first_name,
                    last_name=data.last_name,
                    department=data.department,
                    position=data.position,
                    email=str(data.email) if data.email else None,
                    phone=data.phone,
                    status=status_enum,
                )
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
