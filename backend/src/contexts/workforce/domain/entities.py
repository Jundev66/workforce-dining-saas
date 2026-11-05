from datetime import datetime
from typing import Optional
import uuid

from src.shared.domain.base import AggregateRoot, utc_now
from src.contexts.workforce.domain.value_objects import (
    DocumentId,
    BadgeCode,
    Department,
    EmployeeStatus,
)
from src.contexts.workforce.domain.events import (
    EmployeeOnboardedDomainEvent,
    EmployeeStatusChangedDomainEvent,
)


class Employee(AggregateRoot):
    def __init__(
        self,
        id: str,
        tenant_id: str,
        first_name: str,
        last_name: str,
        document_id: DocumentId,
        department: Department,
        badge_code: BadgeCode,
        position: str = "Employee",
        email: Optional[str] = None,
        phone: Optional[str] = None,
        status: EmployeeStatus = EmployeeStatus.ACTIVE,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__()
        self.id = id
        self.tenant_id = tenant_id
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        self.document_id = document_id
        self.department = department
        self.badge_code = badge_code
        self.position = position.strip()
        self.email = email.lower().strip() if email else None
        self.phone = phone.strip() if phone else None
        self.status = status
        self.created_at = created_at or utc_now()
        self.updated_at = updated_at or utc_now()

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
        department: str = "General",
        position: str = "Employee",
        email: Optional[str] = None,
        phone: Optional[str] = None,
        badge_code: Optional[str] = None,
    ) -> "Employee":
        if not first_name or len(first_name.strip()) < 1:
            raise ValueError("First name cannot be empty.")
        if not last_name or len(last_name.strip()) < 1:
            raise ValueError("Last name cannot be empty.")

        emp_id = str(uuid.uuid4())
        doc_vo = DocumentId(document_id)
        dept_vo = Department(department)
        badge_val = badge_code.strip() if badge_code else f"EMP-{uuid.uuid4().hex[:8].upper()}"
        badge_vo = BadgeCode(badge_val)

        employee = cls(
            id=emp_id,
            tenant_id=tenant_id,
            first_name=first_name,
            last_name=last_name,
            document_id=doc_vo,
            department=dept_vo,
            badge_code=badge_vo,
            position=position,
            email=email,
            phone=phone,
            status=EmployeeStatus.ACTIVE,
        )

        employee.record_event(
            EmployeeOnboardedDomainEvent(
                employee_id=emp_id,
                tenant_id=tenant_id,
                document_id=str(doc_vo),
                badge_code=str(badge_vo),
            )
        )
        return employee

    def update_profile(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        department: Optional[str] = None,
        position: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> None:
        if first_name is not None:
            if not first_name.strip():
                raise ValueError("First name cannot be empty.")
            self.first_name = first_name.strip()
        if last_name is not None:
            if not last_name.strip():
                raise ValueError("Last name cannot be empty.")
            self.last_name = last_name.strip()
        if department is not None:
            self.department = Department(department)
        if position is not None:
            self.position = position.strip()
        if email is not None:
            self.email = email.lower().strip() if email else None
        if phone is not None:
            self.phone = phone.strip() if phone else None
        self.updated_at = utc_now()

    def change_status(self, new_status: EmployeeStatus) -> None:
        if self.status != new_status:
            prev = self.status.value
            self.status = new_status
            self.updated_at = utc_now()
            self.record_event(
                EmployeeStatusChangedDomainEvent(
                    employee_id=self.id,
                    tenant_id=self.tenant_id,
                    previous_status=prev,
                    new_status=new_status.value,
                )
            )
