from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.contexts.iam.domain.entities import Tenant, User
from src.contexts.iam.domain.value_objects import TenantSlug, EmailAddress, UserRole
from src.contexts.iam.domain.ports import TenantRepository, UserRepository
from src.contexts.iam.infrastructure.persistence.models import TenantModel, UserModel
from src.shared.infrastructure.tenant_context import get_current_tenant_id


class SQLAlchemyTenantRepository(TenantRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: TenantModel) -> Tenant:
        return Tenant(
            id=model.id,
            name=model.name,
            slug=TenantSlug(model.slug),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        stmt = select(TenantModel).where(TenantModel.id == tenant_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        stmt = select(TenantModel).where(TenantModel.slug == slug.lower().strip())
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def create(self, tenant: Tenant) -> Tenant:
        model = TenantModel(
            id=tenant.id,
            name=tenant.name,
            slug=str(tenant.slug),
            is_active=tenant.is_active,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=model.id,
            tenant_id=model.tenant_id,
            email=EmailAddress(model.email),
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            role=UserRole(model.role),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, user_id: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == user_id)
        tenant_id = get_current_tenant_id()
        if tenant_id:
            stmt = stmt.where(UserModel.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email.lower().strip())
        tenant_id = get_current_tenant_id()
        if tenant_id:
            stmt = stmt.where(UserModel.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def create(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            tenant_id=user.tenant_id,
            email=str(user.email),
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)
