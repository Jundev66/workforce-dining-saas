from pydantic import BaseModel, EmailStr, Field


class RegisterTenantRequest(BaseModel):
    tenant_name: str = Field(..., min_length=2, max_length=100, examples=["Acme Corp"])
    tenant_slug: str = Field(..., min_length=2, max_length=50, examples=["acme"])
    admin_email: EmailStr = Field(..., examples=["admin@acme.com"])
    admin_password: str = Field(..., min_length=8, examples=["SecurePass123!"])
    admin_full_name: str = Field(..., min_length=2, max_length=150, examples=["John Doe"])


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., examples=["admin@acme.com"])
    password: str = Field(..., examples=["SecurePass123!"])
    tenant_slug: str | None = Field(default=None, examples=["acme"])


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    tenant_id: str
    role: str
    full_name: str
    email: str
