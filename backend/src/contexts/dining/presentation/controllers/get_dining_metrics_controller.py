from typing import Dict, Any
from fastapi import Depends

from src.contexts.dining.application.use_cases.get_dining_metrics_use_case import GetDiningMetricsUseCase
from src.contexts.dining.application.dtos import DiningMetricsDTO
from src.contexts.dining.infrastructure.persistence.repositories import SQLAlchemyMealRepository
from src.contexts.dining.presentation.controllers.common import (
    get_meal_repo,
    get_current_user,
)


class GetDiningMetricsController:
    """Single-Action Controller: Retrieves real-time dining hall stats for the active tenant."""

    @staticmethod
    async def handle(
        current_user: Dict[str, Any] = Depends(get_current_user),
        meal_repo: SQLAlchemyMealRepository = Depends(get_meal_repo),
    ) -> DiningMetricsDTO:
        use_case = GetDiningMetricsUseCase(meal_repo)
        return await use_case.execute(current_user["tenant_id"])
