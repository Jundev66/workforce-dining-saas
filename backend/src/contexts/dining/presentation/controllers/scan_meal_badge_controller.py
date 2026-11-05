from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.contexts.dining.application.use_cases.scan_meal_badge_use_case import ScanMealBadgeUseCase
from src.contexts.dining.application.dtos import ScanMealBadgeCommand, MealScanResultDTO
from src.contexts.dining.infrastructure.persistence.repositories import SQLAlchemyMealRepository
from src.contexts.workforce.infrastructure.persistence.repositories import SQLAlchemyEmployeeRepository
from src.contexts.dining.presentation.controllers.common import (
    get_meal_repo,
    get_employee_repo,
    get_current_user,
)


class ScanMealBadgeRequest(BaseModel):
    badge_code: str = Field(..., min_length=2, max_length=100)
    meal_type: str = Field(default="lunch")
    notes: Optional[str] = None


class ScanMealBadgeController:
    """Single-Action Controller: Processes an employee QR badge scan at the dining hall."""

    @staticmethod
    async def handle(
        data: ScanMealBadgeRequest,
        current_user: Dict[str, Any] = Depends(get_current_user),
        meal_repo: SQLAlchemyMealRepository = Depends(get_meal_repo),
        employee_repo: SQLAlchemyEmployeeRepository = Depends(get_employee_repo),
    ) -> MealScanResultDTO:
        use_case = ScanMealBadgeUseCase(
            meal_repo=meal_repo,
            employee_repo=employee_repo,
        )
        try:
            return await use_case.execute(
                ScanMealBadgeCommand(
                    tenant_id=current_user["tenant_id"],
                    badge_code=data.badge_code,
                    meal_type=data.meal_type,
                    notes=data.notes,
                )
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
