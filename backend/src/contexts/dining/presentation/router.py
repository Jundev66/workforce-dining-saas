from fastapi import APIRouter
from src.contexts.dining.presentation.controllers.common import (
    get_meal_repo,
    get_dining_ai_predictor,
    get_current_user,
)
from src.contexts.dining.application.dtos import (
    MealScanResultDTO,
    DiningMetricsDTO,
    AiForecastDTO,
)
from src.contexts.dining.presentation.controllers.scan_meal_badge_controller import (
    ScanMealBadgeController,
)
from src.contexts.dining.presentation.controllers.get_dining_metrics_controller import (
    GetDiningMetricsController,
)
from src.contexts.dining.presentation.controllers.forecast_dining_demand_controller import (
    ForecastDiningDemandController,
)

router = APIRouter(prefix="/dining", tags=["Dining - Meal Tracking & AI Automation"])

router.add_api_route(
    "/scan",
    ScanMealBadgeController.handle,
    methods=["POST"],
    response_model=MealScanResultDTO,
    summary="Scan QR badge for meal entitlement",
)

router.add_api_route(
    "/metrics/today",
    GetDiningMetricsController.handle,
    methods=["GET"],
    response_model=DiningMetricsDTO,
    summary="Get today's dining metrics",
)

router.add_api_route(
    "/ai/forecast",
    ForecastDiningDemandController.handle,
    methods=["GET"],
    response_model=AiForecastDTO,
    summary="AI forecast for meal demand and portion prep",
)

__all__ = ["router", "get_meal_repo", "get_dining_ai_predictor", "get_current_user"]
