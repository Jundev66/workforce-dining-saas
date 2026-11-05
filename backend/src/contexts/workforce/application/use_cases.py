from typing import Optional, List
from src.contexts.workforce.domain.entities import Employee
from src.contexts.workforce.domain.value_objects import EmployeeStatus
from src.contexts.workforce.domain.ports import EmployeeRepository
from src.contexts.workforce.application.dtos import (
    CreateEmployeeCommand,
    UpdateEmployeeCommand,
    EmployeeDTO,
    PaginatedEmployeesDTO,
)


def _to_dto(emp: Employee) -> EmployeeDTO:
    return EmployeeDTO(
        id=emp.id,
        tenant_id=emp.tenant_id,
        first_name=emp.first_name,
        last_name=emp.last_name,
        full_name=emp.full_name,
        document_id=str(emp.document_id),
        department=str(emp.department),
        position=emp.position,
        status=emp.status.value,
        badge_code=str(emp.badge_code),
        email=emp.email,
        phone=emp.phone,
        created_at=emp.created_at,
        updated_at=emp.updated_at,
    )


class CreateEmployeeUseCase:
    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo

    async def execute(self, cmd: CreateEmployeeCommand) -> EmployeeDTO:
        # Check uniqueness of document_id
        existing_doc = await self.employee_repo.get_by_document_id(cmd.document_id)
        if existing_doc:
            raise ValueError(f"Employee with document ID '{cmd.document_id}' already exists in this organization.")

        if cmd.badge_code:
            existing_badge = await self.employee_repo.get_by_badge_code(cmd.badge_code)
            if existing_badge:
                raise ValueError(f"Badge code '{cmd.badge_code}' is already assigned to another employee.")

        # Create Aggregate Root (fires EmployeeOnboardedDomainEvent)
        employee = Employee.create(
            tenant_id=cmd.tenant_id,
            first_name=cmd.first_name,
            last_name=cmd.last_name,
            document_id=cmd.document_id,
            department=cmd.department,
            position=cmd.position,
            email=cmd.email,
            phone=cmd.phone,
            badge_code=cmd.badge_code,
        )

        saved = await self.employee_repo.create(employee)
        return _to_dto(saved)


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
    ) -> PaginatedEmployeesDTO:
        items, total = await self.employee_repo.list(
            skip=skip,
            limit=limit,
            department=department,
            status=status,
            search=search,
        )
        return PaginatedEmployeesDTO(
            items=[_to_dto(e) for e in items],
            total=total,
            skip=skip,
            limit=limit,
        )


class GetEmployeeDetailUseCase:
    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo

    async def execute(self, employee_id: str) -> EmployeeDTO:
        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee with ID '{employee_id}' not found.")
        return _to_dto(employee)


class UpdateEmployeeUseCase:
    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo

    async def execute(self, cmd: UpdateEmployeeCommand) -> EmployeeDTO:
        employee = await self.employee_repo.get_by_id(cmd.employee_id)
        if not employee:
            raise ValueError(f"Employee with ID '{cmd.employee_id}' not found.")

        employee.update_profile(
            first_name=cmd.first_name,
            last_name=cmd.last_name,
            department=cmd.department,
            position=cmd.position,
            email=cmd.email,
            phone=cmd.phone,
        )

        if cmd.status is not None:
            employee.change_status(cmd.status)

        saved = await self.employee_repo.update(employee)
        return _to_dto(saved)


class DeleteEmployeeUseCase:
    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo

    async def execute(self, employee_id: str) -> bool:
        success = await self.employee_repo.delete(employee_id)
        if not success:
            raise ValueError(f"Employee with ID '{employee_id}' not found.")
        return True
