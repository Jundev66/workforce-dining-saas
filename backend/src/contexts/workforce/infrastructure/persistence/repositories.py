from typing import List, Optional, Tuple
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.contexts.workforce.domain.entities import Employee
from src.contexts.workforce.domain.value_objects import (
    DocumentId,
    BadgeCode,
    Department,
    EmployeeStatus,
)
from src.contexts.workforce.domain.ports import EmployeeRepository
from src.contexts.workforce.infrastructure.persistence.models import EmployeeModel
from src.shared.infrastructure.tenant_context import get_current_tenant_id


class SQLAlchemyEmployeeRepository(EmployeeRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: EmployeeModel) -> Employee:
        return Employee(
            id=model.id,
            tenant_id=model.tenant_id,
            first_name=model.first_name,
            last_name=model.last_name,
            document_id=DocumentId(model.document_id),
            department=Department(model.department),
            badge_code=BadgeCode(model.badge_code or ""),
            position=model.position,
            email=model.email,
            phone=model.phone,
            status=EmployeeStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _base_query(self):
        stmt = select(EmployeeModel)
        tenant_id = get_current_tenant_id()
        if tenant_id:
            stmt = stmt.where(EmployeeModel.tenant_id == tenant_id)
        return stmt

    async def get_by_id(self, employee_id: str) -> Optional[Employee]:
        stmt = self._base_query().where(EmployeeModel.id == employee_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_document_id(self, document_id: str) -> Optional[Employee]:
        stmt = self._base_query().where(EmployeeModel.document_id == document_id.strip().upper())
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_badge_code(self, badge_code: str) -> Optional[Employee]:
        stmt = self._base_query().where(EmployeeModel.badge_code == badge_code.strip().upper())
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        department: Optional[str] = None,
        status: Optional[EmployeeStatus] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Employee], int]:
        tenant_id = get_current_tenant_id()
        filters = []
        if tenant_id:
            filters.append(EmployeeModel.tenant_id == tenant_id)
        if department:
            filters.append(EmployeeModel.department.ilike(f"%{department.strip()}%"))
        if status:
            filters.append(EmployeeModel.status == status.value)
        if search:
            term = f"%{search.strip()}%"
            filters.append(
                or_(
                    EmployeeModel.first_name.ilike(term),
                    EmployeeModel.last_name.ilike(term),
                    EmployeeModel.document_id.ilike(term),
                    EmployeeModel.email.ilike(term),
                    EmployeeModel.badge_code.ilike(term),
                )
            )

        count_stmt = select(func.count()).select_from(EmployeeModel)
        if filters:
            count_stmt = count_stmt.where(*filters)
        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar_one()

        items_stmt = select(EmployeeModel)
        if filters:
            items_stmt = items_stmt.where(*filters)
        items_stmt = items_stmt.order_by(EmployeeModel.created_at.desc()).offset(skip).limit(limit)

        res = await self.session.execute(items_stmt)
        models = res.scalars().all()
        return [self._to_domain(m) for m in models], total

    async def create(self, employee: Employee) -> Employee:
        model = EmployeeModel(
            id=employee.id,
            tenant_id=employee.tenant_id,
            first_name=employee.first_name,
            last_name=employee.last_name,
            document_id=str(employee.document_id),
            department=str(employee.department),
            badge_code=str(employee.badge_code),
            position=employee.position,
            email=employee.email,
            phone=employee.phone,
            status=employee.status.value,
            created_at=employee.created_at,
            updated_at=employee.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def update(self, employee: Employee) -> Employee:
        stmt = select(EmployeeModel).where(EmployeeModel.id == employee.id)
        tenant_id = get_current_tenant_id()
        if tenant_id:
            stmt = stmt.where(EmployeeModel.tenant_id == tenant_id)
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        if not model:
            raise ValueError(f"Employee {employee.id} not found.")

        model.first_name = employee.first_name
        model.last_name = employee.last_name
        model.document_id = str(employee.document_id)
        model.department = str(employee.department)
        model.badge_code = str(employee.badge_code)
        model.position = employee.position
        model.email = employee.email
        model.phone = employee.phone
        model.status = employee.status.value
        model.updated_at = employee.updated_at

        await self.session.flush()
        return self._to_domain(model)

    async def delete(self, employee_id: str) -> bool:
        stmt = select(EmployeeModel).where(EmployeeModel.id == employee_id)
        tenant_id = get_current_tenant_id()
        if tenant_id:
            stmt = stmt.where(EmployeeModel.tenant_id == tenant_id)
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.flush()
        return True
