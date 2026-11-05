from dataclasses import dataclass
from typing import List, Optional, Tuple
from src.domain.models.employee import Employee, EmployeeStatus
from src.domain.ports.employee_repository import EmployeeRepository


@dataclass
class CreateEmployeeCommand:
    tenant_id: str
    first_name: str
    last_name: str
    document_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    department: str = "General"
    position: str = "Employee"
    badge_code: Optional[str] = None


@dataclass
class UpdateEmployeeCommand:
    employee_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    status: Optional[EmployeeStatus] = None


class CreateEmployeeUseCase:
    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo

    async def execute(self, cmd: CreateEmployeeCommand) -> Employee:
        existing_doc = await self.employee_repo.get_by_document_id(cmd.document_id)
        if existing_doc:
            raise ValueError(f"Employee with document ID '{cmd.document_id}' already exists in this tenant")

        if cmd.badge_code:
            existing_badge = await self.employee_repo.get_by_badge_code(cmd.badge_code)
            if existing_badge:
                raise ValueError(f"Badge code '{cmd.badge_code}' is already assigned to another employee")

        employee = Employee.create(
            tenant_id=cmd.tenant_id,
            first_name=cmd.first_name,
            last_name=cmd.last_name,
            document_id=cmd.document_id,
            email=cmd.email,
            phone=cmd.phone,
            department=cmd.department,
            position=cmd.position,
            badge_code=cmd.badge_code,
        )
        return await self.employee_repo.create(employee)


class ListEmployeesUseCase:
    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        department: Optional[str] = None,
        status: Optional[EmployeeStatus] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Employee], int]:
        return await self.employee_repo.list(
            skip=skip,
            limit=limit,
            department=department,
            status=status,
            search=search,
        )


class GetEmployeeDetailUseCase:
    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo

    async def execute(self, employee_id: str) -> Employee:
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee with ID '{employee_id}' not found")
        return employee


class UpdateEmployeeUseCase:
    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo

    async def execute(self, cmd: UpdateEmployeeCommand) -> Employee:
        employee = await self.employee_repo.get_by_id(cmd.employee_id)
        if not employee:
            raise ValueError(f"Employee with ID '{cmd.employee_id}' not found")

        employee.update(
            first_name=cmd.first_name,
            last_name=cmd.last_name,
            email=cmd.email,
            phone=cmd.phone,
            department=cmd.department,
            position=cmd.position,
            status=cmd.status,
        )
        return await self.employee_repo.update(employee)


class DeleteEmployeeUseCase:
    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo

    async def execute(self, employee_id: str) -> bool:
        success = await self.employee_repo.delete(employee_id)
        if not success:
            raise ValueError(f"Employee with ID '{employee_id}' not found")
        return True
