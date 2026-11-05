import re
from dataclasses import dataclass
from enum import Enum
from src.shared.domain.base import ValueObject


@dataclass(frozen=True)
class TenantSlug(ValueObject):
    value: str

    def __post_init__(self):
        cleaned = self.value.strip().lower()
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", cleaned):
            raise ValueError(f"Invalid tenant slug '{self.value}'. Must be alphanumeric lowercase with hyphens.")
        if len(cleaned) < 2 or len(cleaned) > 50:
            raise ValueError(f"Tenant slug length must be between 2 and 50 characters, got {len(cleaned)}.")
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class EmailAddress(ValueObject):
    value: str

    def __post_init__(self):
        cleaned = self.value.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", cleaned):
            raise ValueError(f"Invalid email address '{self.value}'.")
        object.__setattr__(self, "value", cleaned)

    def __str__(self) -> str:
        return self.value


class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
