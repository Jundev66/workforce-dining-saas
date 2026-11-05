from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RegisterTenantCommand:
    tenant_name: str
    tenant_slug: str
    admin_email: str
    admin_password: str
    admin_full_name: str


@dataclass(frozen=True)
class LoginCommand:
    email: str
    password: str
    tenant_slug: Optional[str] = None


@dataclass(frozen=True)
class AuthResponseDTO:
    access_token: str
    token_type: str
    user_id: str
    tenant_id: str
    role: str
    full_name: str
    email: str
