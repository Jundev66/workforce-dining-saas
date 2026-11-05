from abc import ABC, abstractmethod
from typing import Optional
from src.contexts.iam.domain.entities import Tenant, User


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


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        pass
