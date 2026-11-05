from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.core.context import set_current_tenant_id


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Extracts the tenant identifier from request headers or auth context
    and injects it into the execution context for downstream services and DB sessions.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Check X-Tenant-ID header first (common in mobile clients and API integrations)
        tenant_id = request.headers.get("X-Tenant-ID")

        # Set tenant in ContextVar
        set_current_tenant_id(tenant_id)

        try:
            response = await call_next(request)
            return response
        finally:
            # Clean up context at the end of the request cycle
            set_current_tenant_id(None)
