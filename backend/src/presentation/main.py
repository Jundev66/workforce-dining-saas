from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.presentation.middlewares.tenant_middleware import TenantMiddleware
from src.presentation.api.v1.routers.health import router as health_router

app = FastAPI(
    title="Staff Attendance & Dining SaaS API",
    description="Multi-tenant backend for workforce attendance, dining hall tracking, and AI-driven automation.",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Multi-tenant isolation middleware
app.add_middleware(TenantMiddleware)

# Include Routers
app.include_router(health_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Staff Attendance & Dining SaaS API",
        "docs": "/docs",
        "status": "operational",
    }
