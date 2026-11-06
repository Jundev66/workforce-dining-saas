from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.shared.infrastructure.config import settings
from src.shared.infrastructure.middlewares.tenant_middleware import TenantMiddleware
from src.shared.infrastructure.middlewares.idempotency_middleware import IdempotencyMiddleware
from src.contexts.iam.presentation.router import router as iam_router
from src.contexts.workforce.presentation.router import router as workforce_router
from src.contexts.dining.presentation.router import router as dining_router
from src.contexts.copilot.presentation.router import router as copilot_router
from src.contexts.dining.infrastructure.realtime.dining_event_subscriber import (
    register_dining_subscribers,
)

# Wire domain event subscribers
register_dining_subscribers()

app = FastAPI(
    title="Workforce Attendance & Dining SaaS API",
    description="Multi-tenant backend built with Screaming Architecture, Tactical DDD, and PostgreSQL RLS.",
    version="2.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Multi-tenant isolation
app.add_middleware(TenantMiddleware)

# Distributed idempotency protection
app.add_middleware(IdempotencyMiddleware)

# CORS (Outermost middleware to handle all preflights and errors with proper origin reflection)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Bounded Context Routers
app.include_router(iam_router, prefix="/api/v1")
app.include_router(workforce_router, prefix="/api/v1")
app.include_router(dining_router, prefix="/api/v1")
app.include_router(copilot_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "architecture": "Screaming DDD"}


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": "Workforce & Dining SaaS API",
        "docs": "/docs",
        "status": "operational",
    }
