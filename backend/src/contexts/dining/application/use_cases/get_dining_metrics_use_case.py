from datetime import datetime, timezone
from src.contexts.dining.domain.ports import MealRepository
from src.contexts.dining.application.dtos import DiningMetricsDTO


class GetDiningMetricsUseCase:
    """Use Case: Calculates real-time metrics of meals consumed today."""

    def __init__(self, meal_repo: MealRepository):
        self.meal_repo = meal_repo

    async def execute(self, tenant_id: str) -> DiningMetricsDTO:
        today = datetime.now(timezone.utc).date()
        metrics = await self.meal_repo.get_daily_metrics(tenant_id, today)

        breakfast = metrics.get("breakfast", 0)
        lunch = metrics.get("lunch", 0)
        dinner = metrics.get("dinner", 0)
        rejected = metrics.get("rejected", 0)
        total = breakfast + lunch + dinner

        return DiningMetricsDTO(
            total_meals_today=total,
            breakfast_count=breakfast,
            lunch_count=lunch,
            dinner_count=dinner,
            rejected_count=rejected,
        )
