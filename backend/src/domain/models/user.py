from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid


class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"


@dataclass
class User:
    id: str
    tenant_id: str
    email: str
    hashed_password: str
    full_name: str
    role: UserRole = UserRole.ADMIN
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        tenant_id: str,
        email: str,
        hashed_password: str,
        full_name: str,
        role: UserRole = UserRole.ADMIN,
    ) -> "User":
        now = datetime.now(timezone.utc)
        return cls(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            email=email.lower().strip(),
            hashed_password=hashed_password,
            full_name=full_name.strip(),
            role=role,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
