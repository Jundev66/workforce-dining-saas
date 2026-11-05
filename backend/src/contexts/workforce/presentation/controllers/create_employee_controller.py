from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from src.contexts.workforce.application.use_cases.create_employee_use_case import CreateEmployeeUseCase
from src.contexts.workforce.application.dtos import CreateEmployeeCommand, EmployeeDTO
from src.contexts.workforce.infrastructure.persistence.repositories import SQLAlchemyEmployeeRepository
from src.contexts.workforce.presentation.controllers.common import (
    get_employee_repo,
    get_current_user,
)


class EmployeeCreateRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    document_id: str = Field(..., min_length=3, max_length=50)
    department: str = Field(default="General", max_length=100)
    position: str = Field(default="Employee", max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    badge_code: Optional[str] = Field(default=None, max_length=100)


class CreateEmployeeController:
    """Single-Action Controller: Handles onboarding a new employee with domain verification."""

    @staticmethod
    async def handle(
        data: EmployeeCreateRequest,
        current_user: Dict[str, Any] = Depends(get_current_user),
        repo: SQLAlchemyEmployeeRepository = Depends(get_employee_repo),
    ) -> EmployeeDTO:
        use_case = CreateEmployeeUseCase(repo)
        try:
            return await use_case.execute(
                CreateEmployeeCommand(
                    tenant_id=current_user["tenant_id"],
                    first_name=data.first_name,
                    last_name=data.last_name,
                    document_id=data.document_id,
                    department=data.department,
                    position=data.position,
                    email=str(data.email) if data.email else None,
                    phone=data.phone,
                    badge_code=data.badge_code,
                )
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
