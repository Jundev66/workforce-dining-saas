from contextvars import ContextVar
from typing import Optional

# Holds the current active tenant identifier for the async request scope
_current_tenant_id: ContextVar[Optional[str]] = ContextVar("current_tenant_id", default=None)


def get_current_tenant_id() -> Optional[str]:
    """Retrieve the tenant ID associated with the current execution context."""
    return _current_tenant_id.get()


def set_current_tenant_id(tenant_id: Optional[str]) -> None:
    """Assign the tenant ID for the current execution context."""
    _current_tenant_id.set(tenant_id)
