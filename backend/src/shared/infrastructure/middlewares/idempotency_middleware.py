import time
from typing import Dict, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.datastructures import Headers


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces idempotent execution for mutating requests (POST, PUT, PATCH).
    Prevents duplicate operations when network retries or double clicks submit the same X-Idempotency-Key.
    """

    def __init__(self, app, ttl_seconds: int = 600):
        super().__init__(app)
        self.ttl_seconds = ttl_seconds
        # Key: (tenant_id or "global", idempotency_key) -> (status_code, body_bytes, headers_dict, timestamp)
        self._cache: Dict[Tuple[str, str], Tuple[int, bytes, Dict[str, str], float]] = {}
        # Tracks keys currently executing to prevent simultaneous race conditions
        self._inflight: set[Tuple[str, str]] = set()

    def _cleanup_expired(self, now: float) -> None:
        expired = [k for k, v in self._cache.items() if now - v[3] > self.ttl_seconds]
        for k in expired:
            del self._cache[k]

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method not in ("POST", "PUT", "PATCH"):
            return await call_next(request)

        idempotency_key = request.headers.get("X-Idempotency-Key") or request.headers.get("Idempotency-Key")
        if not idempotency_key:
            return await call_next(request)

        tenant_id = request.headers.get("X-Tenant-ID") or "global"
        cache_key = (tenant_id, idempotency_key.strip())
        now = time.time()

        self._cleanup_expired(now)

        # 1. Race condition check: identical key is currently being processed
        if cache_key in self._inflight:
            return JSONResponse(
                status_code=409,
                content={"detail": "Operación concurrente en progreso con la misma Idempotency-Key."},
            )

        # 2. Replay check: identical key has already succeeded
        if cache_key in self._cache:
            status_code, body, cached_headers, _ = self._cache[cache_key]
            return Response(
                content=body,
                status_code=status_code,
                headers=dict(cached_headers),
                media_type="application/json",
            )

        # Mark key as inflight
        self._inflight.add(cache_key)

        try:
            response = await call_next(request)

            # Only cache successful responses (2xx or 4xx domain errors, not 5xx)
            if response.status_code < 500:
                body = [section async for section in response.body_iterator]
                response_body = b"".join(body)

                response_headers = {
                    k: v for k, v in response.headers.items()
                    if k.lower() not in ("content-length", "content-encoding")
                }
                response_headers["X-Cache-Lookup"] = "HIT-IDEMPOTENT"

                self._cache[cache_key] = (
                    response.status_code,
                    response_body,
                    response_headers,
                    time.time(),
                )

                return Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=response_headers,
                    media_type=response.media_type,
                )

            return response
        finally:
            self._inflight.discard(cache_key)
