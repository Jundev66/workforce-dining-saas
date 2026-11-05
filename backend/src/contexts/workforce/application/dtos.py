from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from src.contexts.workforce.domain.value_objects import EmployeeStatus


@dataclass(frozen=True)
class CreateEmployeeCommand:
    tenant_id: str
    first_name: str
    last_name: str
    document_id: str
    department: str = "General"
    position: str = "Employee"
    email: Optional[str] = None
    phone: Optional[str] = None
    badge_code: Optional[str] = None


@dataclass(frozen=True)
class UpdateEmployeeCommand:
    employee_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[EmployeeStatus] = None


@dataclass(frozen=True)
class EmployeeDTO:
    id: str
    tenant_id: str
    first_name: str
    last_name: str
    full_name: str
    document_id: str
    department: str
    position: str
    status: str
    badge_code: str
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass(frozen=True)
class PaginatedEmployeesDTO:
    items: List[EmployeeDTO]
    total: int
    skip: int
    limit: int
