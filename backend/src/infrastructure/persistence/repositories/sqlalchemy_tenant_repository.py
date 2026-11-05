from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.tenant import Tenant
from src.domain.ports.tenant_repository import TenantRepository
from src.infrastructure.persistence.models.tenant_model import TenantModel


class SQLAlchemyTenantRepository(TenantRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: TenantModel) -> Tenant:
        return Tenant(
            id=model.id,
            name=model.name,
            slug=model.slug,
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
            slug=tenant.slug,
            is_active=tenant.is_active,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)
