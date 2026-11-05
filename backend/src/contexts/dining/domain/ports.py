from abc import ABC, abstractmethod
from datetime import date
from typing import Dict, List, Optional, Any
from src.contexts.dining.domain.entities import MealRecord
from src.contexts.dining.domain.value_objects import MealType


class MealRepository(ABC):
    @abstractmethod
    async def save(self, meal: MealRecord) -> MealRecord:
        pass

    @abstractmethod
    async def has_consumed_meal_on_date(
        self,
        employee_id: str,
        meal_type: MealType,
        target_date: date,
    ) -> bool:
        """Returns True if the employee has already consumed this meal type on the given date."""
        pass

    @abstractmethod
    async def get_daily_metrics(
        self,
        tenant_id: str,
        target_date: date,
    ) -> Dict[str, int]:
        """Returns a breakdown of meals served today by meal type and status."""
        pass

    @abstractmethod
    async def list_recent(
        self,
        skip: int = 0,
        limit: int = 50,
    ) -> List[MealRecord]:
        pass


class DiningAiPredictorPort(ABC):
    """Port for AI-driven dining room headcount forecasting and portion optimization."""

    @abstractmethod
    async def predict_demand(
        self,
        active_staff_count: int,
        day_of_week: int,
        historical_ratios: Dict[str, float],
    ) -> Dict[str, Any]:
        pass
