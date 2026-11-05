from typing import Dict, Any
from fastapi import Depends

from src.contexts.dining.application.use_cases.forecast_dining_demand_use_case import ForecastDiningDemandUseCase
from src.contexts.dining.application.dtos import AiForecastDTO
from src.contexts.workforce.infrastructure.persistence.repositories import SQLAlchemyEmployeeRepository
from src.contexts.dining.infrastructure.external.ai_predictor_service import HeuristicAiDiningPredictor
from src.contexts.dining.presentation.controllers.common import (
    get_employee_repo,
    get_dining_ai_predictor,
    get_current_user,
)


class ForecastDiningDemandController:
    """Single-Action Controller: Provides AI-driven dining room headcount forecasting."""

    @staticmethod
    async def handle(
        current_user: Dict[str, Any] = Depends(get_current_user),
        employee_repo: SQLAlchemyEmployeeRepository = Depends(get_employee_repo),
        ai_predictor: HeuristicAiDiningPredictor = Depends(get_dining_ai_predictor),
    ) -> AiForecastDTO:
        use_case = ForecastDiningDemandUseCase(
            employee_repo=employee_repo,
            ai_predictor=ai_predictor,
        )
        return await use_case.execute(current_user["tenant_id"])
