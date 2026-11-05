from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, List


@dataclass(frozen=True)
class ScanMealBadgeCommand:
    tenant_id: str
    badge_code: str
    meal_type: str = "lunch"
    notes: Optional[str] = None


@dataclass(frozen=True)
class MealScanResultDTO:
    id: str
    status: str
    approved: bool
    employee_id: str
    employee_name: str
    department: str
    meal_type: str
    badge_code: str
    message: str
    consumed_at: datetime


@dataclass(frozen=True)
class DiningMetricsDTO:
    total_meals_today: int
    breakfast_count: int
    lunch_count: int
    dinner_count: int
    rejected_count: int


@dataclass(frozen=True)
class AiForecastDTO:
    date: str
    active_workforce_count: int
    forecasted_lunch_headcount: int
    forecasted_breakfast_headcount: int
    recommended_food_prep_kg: float
    confidence_score: float
    insights: List[str]
