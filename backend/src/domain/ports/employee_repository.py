from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from src.domain.models.employee import Employee, EmployeeStatus


class EmployeeRepository(ABC):
    @abstractmethod
    async def get_by_id(self, employee_id: str) -> Optional[Employee]:
        pass

    @abstractmethod
    async def get_by_document_id(self, document_id: str) -> Optional[Employee]:
        pass

    @abstractmethod
    async def get_by_badge_code(self, badge_code: str) -> Optional[Employee]:
        pass

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        department: Optional[str] = None,
        status: Optional[EmployeeStatus] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Employee], int]:
        """Returns a tuple containing (items, total_count)."""
        pass

    @abstractmethod
    async def create(self, employee: Employee) -> Employee:
        pass

    @abstractmethod
    async def update(self, employee: Employee) -> Employee:
        pass

    @abstractmethod
    async def delete(self, employee_id: str) -> bool:
        pass
