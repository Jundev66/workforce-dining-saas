from fastapi import APIRouter, status
from src.contexts.iam.application.dtos import AuthResponseDTO
from src.contexts.iam.presentation.controllers.register_tenant_controller import (
    RegisterTenantController,
    get_tenant_repo,
    get_user_repo,
)
from src.contexts.iam.presentation.controllers.login_controller import (
    LoginController,
)

router = APIRouter(prefix="/auth", tags=["IAM - Multi-Tenant Authentication"])

# Register Single-Action Controller endpoints
router.add_api_route(
    "/register-tenant",
    RegisterTenantController.handle,
    methods=["POST"],
    response_model=AuthResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register tenant & admin",
)

router.add_api_route(
    "/login",
    LoginController.handle,
    methods=["POST"],
    response_model=AuthResponseDTO,
    summary="User login",
)

__all__ = ["router", "get_tenant_repo", "get_user_repo"]
