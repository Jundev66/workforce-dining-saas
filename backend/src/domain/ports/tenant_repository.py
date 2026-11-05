from abc import ABC, abstractmethod
from typing import Optional
from src.domain.models.tenant import Tenant


class TenantRepository(ABC):
    @abstractmethod
    async def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        pass

    @abstractmethod
    async def create(self, tenant: Tenant) -> Tenant:
        pass
