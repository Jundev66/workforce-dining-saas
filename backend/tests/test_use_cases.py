import pytest
import asyncio
from typing import Dict, List, Optional, Tuple

from src.domain.models.tenant import Tenant
from src.domain.models.user import User, UserRole
from src.domain.models.employee import Employee, EmployeeStatus
from src.domain.ports.tenant_repository import TenantRepository
from src.domain.ports.user_repository import UserRepository
from src.domain.ports.employee_repository import EmployeeRepository
from src.application.use_cases.auth_use_cases import (
    RegisterTenantUseCase,
    RegisterTenantCommand,
    LoginUseCase,
)
from src.application.use_cases.employee_use_cases import (
    CreateEmployeeUseCase,
    CreateEmployeeCommand,
    ListEmployeesUseCase,
    GetEmployeeDetailUseCase,
    UpdateEmployeeUseCase,
    UpdateEmployeeCommand,
)


class InMemoryTenantRepository(TenantRepository):
    def __init__(self):
        self._tenants: Dict[str, Tenant] = {}

    async def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        return self._tenants.get(tenant_id)

    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        for t in self._tenants.values():
            if t.slug == slug:
                return t
        return None

    async def create(self, tenant: Tenant) -> Tenant:
        self._tenants[tenant.id] = tenant
        return tenant


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._users: Dict[str, User] = {}

    async def get_by_id(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        for u in self._users.values():
            if u.email == email:
                return u
        return None

    async def create(self, user: User) -> User:
        self._users[user.id] = user
        return user


class InMemoryEmployeeRepository(EmployeeRepository):
    def __init__(self):
        self._employees: Dict[str, Employee] = {}

    async def get_by_id(self, employee_id: str) -> Optional[Employee]:
        return self._employees.get(employee_id)

    async def get_by_document_id(self, document_id: str) -> Optional[Employee]:
        for e in self._employees.values():
            if e.document_id == document_id:
                return e
        return None

    async def get_by_badge_code(self, badge_code: str) -> Optional[Employee]:
        for e in self._employees.values():
            if e.badge_code == badge_code:
                return e
        return None

    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        department: Optional[str] = None,
        status: Optional[EmployeeStatus] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Employee], int]:
        items = list(self._employees.values())
        if department:
            items = [e for e in items if department.lower() in e.department.lower()]
        if status:
            items = [e for e in items if e.status == status]
        if search:
            s = search.lower()
            items = [
                e for e in items
                if s in e.first_name.lower() or s in e.last_name.lower() or s in e.document_id.lower()
            ]
        total = len(items)
        return items[skip : skip + limit], total

    async def create(self, employee: Employee) -> Employee:
        self._employees[employee.id] = employee
        return employee

    async def update(self, employee: Employee) -> Employee:
        self._employees[employee.id] = employee
        return employee

    async def delete(self, employee_id: str) -> bool:
        if employee_id in self._employees:
            del self._employees[employee_id]
            return True
        return False


@pytest.mark.asyncio
async def test_register_and_login_tenant():
    tenant_repo = InMemoryTenantRepository()
    user_repo = InMemoryUserRepository()

    reg_use_case = RegisterTenantUseCase(tenant_repo, user_repo)
    login_use_case = LoginUseCase(tenant_repo, user_repo)

    # 1. Register
    reg_dto = await reg_use_case.execute(
        RegisterTenantCommand(
            tenant_name="Industrial Catering S.A.",
            tenant_slug="industrial-catering",
            admin_email="admin@catering.com",
            admin_password="Password123!",
            admin_full_name="Admin Boss",
        )
    )
    assert reg_dto.access_token is not None
    assert reg_dto.email == "admin@catering.com"
    assert reg_dto.role == "admin"

    # 2. Login
    login_dto = await login_use_case.execute(
        email="admin@catering.com",
        password="Password123!",
        tenant_slug="industrial-catering",
    )
    assert login_dto.access_token is not None
    assert login_dto.user_id == reg_dto.user_id


@pytest.mark.asyncio
async def test_employee_crud_use_cases():
    emp_repo = InMemoryEmployeeRepository()
    create_uc = CreateEmployeeUseCase(emp_repo)
    list_uc = ListEmployeesUseCase(emp_repo)
    detail_uc = GetEmployeeDetailUseCase(emp_repo)
    update_uc = UpdateEmployeeUseCase(emp_repo)

    tenant_id = "tenant-123"

    # 1. Create employee
    emp = await create_uc.execute(
        CreateEmployeeCommand(
            tenant_id=tenant_id,
            first_name="Martin",
            last_name="Fierro",
            document_id="DNI-30123456",
            email="martin.fierro@pampa.com",
            department="Cocina",
            position="Jefe de Turno",
            badge_code="QR-001",
        )
    )
    assert emp.id is not None
    assert emp.full_name == "Martin Fierro"
    assert emp.badge_code == "QR-001"
    assert emp.status == EmployeeStatus.ACTIVE

    # 2. List employees
    items, total = await list_uc.execute(search="Martin")
    assert total == 1
    assert items[0].id == emp.id

    # 3. Get Detail
    detail = await detail_uc.execute(emp.id)
    assert detail.document_id == "DNI-30123456"

    # 4. Update
    updated = await update_uc.execute(
        UpdateEmployeeCommand(
            employee_id=emp.id,
            position="Gerente de Comedor",
            status=EmployeeStatus.ACTIVE,
        )
    )
    assert updated.position == "Gerente de Comedor"
