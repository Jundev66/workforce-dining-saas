from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid


class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"


@dataclass
class Employee:
    id: str
    tenant_id: str
    first_name: str
    last_name: str
    document_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    department: str = "General"
    position: str = "Employee"
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    badge_code: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @classmethod
    def create(
        cls,
        tenant_id: str,
        first_name: str,
        last_name: str,
        document_id: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        department: str = "General",
        position: str = "Employee",
        badge_code: Optional[str] = None,
    ) -> "Employee":
        now = datetime.now(timezone.utc)
        generated_badge = badge_code.strip() if badge_code else f"EMP-{uuid.uuid4().hex[:8].upper()}"
        return cls(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            document_id=document_id.strip(),
            email=email.lower().strip() if email else None,
            phone=phone.strip() if phone else None,
            department=department.strip(),
            position=position.strip(),
            status=EmployeeStatus.ACTIVE,
            badge_code=generated_badge,
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        department: Optional[str] = None,
        position: Optional[str] = None,
        status: Optional[EmployeeStatus] = None,
    ) -> None:
        if first_name is not None:
            self.first_name = first_name.strip()
        if last_name is not None:
            self.last_name = last_name.strip()
        if email is not None:
            self.email = email.lower().strip() if email else None
        if phone is not None:
            self.phone = phone.strip() if phone else None
        if department is not None:
            self.department = department.strip()
        if position is not None:
            self.position = position.strip()
        if status is not None:
            self.status = status
        self.updated_at = datetime.now(timezone.utc)
