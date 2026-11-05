from src.contexts.iam.domain.ports import TenantRepository, UserRepository
from src.contexts.iam.application.dtos import LoginCommand, AuthResponseDTO
from src.shared.infrastructure.security import verify_password, create_access_token


class LoginUseCase:
    """Use Case responsible exclusively for authenticating users and issuing access tokens."""

    def __init__(self, tenant_repo: TenantRepository, user_repo: UserRepository):
        self.tenant_repo = tenant_repo
        self.user_repo = user_repo

    async def execute(self, cmd: LoginCommand) -> AuthResponseDTO:
        tenant_id = None
        if cmd.tenant_slug:
            tenant = await self.tenant_repo.get_by_slug(cmd.tenant_slug)
            if not tenant:
                raise ValueError("Tenant not found")
            tenant_id = tenant.id

        user = await self.user_repo.get_by_email(cmd.email)
        if not user:
            raise ValueError("Invalid email or password")

        if tenant_id and user.tenant_id != tenant_id:
            raise ValueError("Invalid credentials for this organization")

        if not verify_password(cmd.password, user.hashed_password):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("User account is inactive")

        token = create_access_token(
            subject=user.id,
            tenant_id=user.tenant_id,
            role=user.role.value,
            extra_claims={"full_name": user.full_name},
        )

        return AuthResponseDTO(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            tenant_id=user.tenant_id,
            role=user.role.value,
            full_name=user.full_name,
            email=str(user.email),
        )
