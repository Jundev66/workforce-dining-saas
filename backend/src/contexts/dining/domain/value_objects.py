from dataclasses import dataclass
from enum import Enum
from src.shared.domain.base import ValueObject


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class MealStatus(str, Enum):
    APPROVED = "approved"
    DUPLICATE_REJECTED = "duplicate_rejected"
    QUOTA_EXCEEDED = "quota_exceeded"


@dataclass(frozen=True)
class MealQuota(ValueObject):
    max_per_day: int = 1

    def __post_init__(self):
        if self.max_per_day < 1:
            raise ValueError("Daily meal quota must be at least 1.")
