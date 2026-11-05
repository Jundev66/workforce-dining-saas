import pytest
from unittest.mock import AsyncMock
from src.contexts.workforce.domain.ports import EmployeeRepository
from src.contexts.dining.domain.ports import DiningAiPredictorPort
from src.contexts.dining.application.use_cases.forecast_dining_demand_use_case import ForecastDiningDemandUseCase


@pytest.mark.asyncio
async def test_should_forecast_dining_demand_using_active_workforce():
    # GIVEN
    employee_repo = AsyncMock(spec=EmployeeRepository)
    employee_repo.list.return_value = ([], 100)  # 100 active staff

    ai_predictor = AsyncMock(spec=DiningAiPredictorPort)
    ai_predictor.predict_demand.return_value = {
        "forecasted_lunch": 82,
        "forecasted_breakfast": 45,
        "recommended_kg": 36.9,
        "confidence": 0.95,
        "insights": ["Demanda alta al mediodía."],
    }

    use_case = ForecastDiningDemandUseCase(employee_repo, ai_predictor)

    # WHEN
    forecast = await use_case.execute("tenant-001")

    # THEN
    assert forecast.active_workforce_count == 100
    assert forecast.forecasted_lunch_headcount == 82
    assert forecast.recommended_food_prep_kg == 36.9
    assert forecast.confidence_score == 0.95

    employee_repo.list.assert_awaited_once()
    ai_predictor.predict_demand.assert_awaited_once()
