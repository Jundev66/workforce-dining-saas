from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import uuid


@dataclass
class Tenant:
    id: str
    name: str
    slug: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def create(cls, name: str, slug: str) -> "Tenant":
        now = datetime.now(timezone.utc)
        return cls(
            id=str(uuid.uuid4()),
            name=name.strip(),
            slug=slug.lower().strip(),
            is_active=True,
            created_at=now,
            updated_at=now,
        )
