from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.shared.infrastructure.tenant_context import set_current_tenant_id


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        tenant_id = request.headers.get("X-Tenant-ID")
        set_current_tenant_id(tenant_id)
        try:
            response = await call_next(request)
            return response
        finally:
            set_current_tenant_id(None)
