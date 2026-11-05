import uuid
from typing import Optional
from src.contexts.workforce.domain.entities import Employee
from src.contexts.workforce.domain.value_objects import EmployeeStatus
from src.contexts.workforce.application.dtos import (
    CreateEmployeeCommand,
    UpdateEmployeeCommand,
)


class EmployeeMother:
    @staticmethod
    def create(
        tenant_id: str = "tenant-001",
        first_name: str = "Julian",
        last_name: str = "Alvarez",
        document_id: str = "DOC-998877",
        department: str = "Comedor",
        position: str = "Cocinero",
        badge_code: str = "BADGE-123",
    ) -> Employee:
        return Employee.create(
            tenant_id=tenant_id,
            first_name=first_name,
            last_name=last_name,
            document_id=document_id,
            department=department,
            position=position,
            badge_code=badge_code,
        )

    @staticmethod
    def random(tenant_id: str = "tenant-001") -> Employee:
        suffix = uuid.uuid4().hex[:6]
        return Employee.create(
            tenant_id=tenant_id,
            first_name=f"Worker{suffix}",
            last_name="Test",
            document_id=f"DNI-{suffix.upper()}",
            department="Operations",
            position="Operator",
            badge_code=f"QR-{suffix.upper()}",
        )


class CreateEmployeeCommandMother:
    @staticmethod
    def create(
        tenant_id: str = "tenant-001",
        first_name: str = "Julian",
        last_name: str = "Alvarez",
        document_id: str = "DOC-998877",
        department: str = "Comedor",
        position: str = "Cocinero",
        badge_code: Optional[str] = "BADGE-123",
    ) -> CreateEmployeeCommand:
        return CreateEmployeeCommand(
            tenant_id=tenant_id,
            first_name=first_name,
            last_name=last_name,
            document_id=document_id,
            department=department,
            position=position,
            badge_code=badge_code,
        )

    @staticmethod
    def random(tenant_id: str = "tenant-001") -> CreateEmployeeCommand:
        suffix = uuid.uuid4().hex[:6]
        return CreateEmployeeCommand(
            tenant_id=tenant_id,
            first_name=f"Worker{suffix}",
            last_name="Test",
            document_id=f"DOC-{suffix.upper()}",
            department="Kitchen",
            position="Chef",
            badge_code=f"QR-{suffix.upper()}",
        )


class UpdateEmployeeCommandMother:
    @staticmethod
    def create(
        employee_id: str,
        first_name: Optional[str] = "UpdatedName",
        last_name: Optional[str] = None,
        department: Optional[str] = "Management",
        position: Optional[str] = "Supervisor",
        status: Optional[EmployeeStatus] = EmployeeStatus.ACTIVE,
    ) -> UpdateEmployeeCommand:
        return UpdateEmployeeCommand(
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            department=department,
            position=position,
            status=status,
        )
