import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from src.shared.domain.base import ValueObject


class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"


@dataclass(frozen=True)
class DocumentId(ValueObject):
    value: str

    def __post_init__(self):
        cleaned = self.value.strip().upper()
        if len(cleaned) < 3 or len(cleaned) > 50:
            raise ValueError(f"Document ID must be between 3 and 50 characters, got '{self.value}'.")
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class BadgeCode(ValueObject):
    value: str

    def __post_init__(self):
        cleaned = self.value.strip().upper()
        if len(cleaned) < 3 or len(cleaned) > 100:
            raise ValueError(f"Badge code must be between 3 and 100 characters, got '{self.value}'.")
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Department(ValueObject):
    value: str

    def __post_init__(self):
        cleaned = self.value.strip()
        if not cleaned:
            cleaned = "General"
        if len(cleaned) > 100:
            raise ValueError(f"Department length exceeds 100 characters.")
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value
