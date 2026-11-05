import uuid
from src.contexts.iam.domain.entities import Tenant
from src.contexts.iam.application.dtos import RegisterTenantCommand
from tests.mothers.value_object_mothers import TenantSlugMother, EmailAddressMother


class TenantMother:
    @staticmethod
    def create(name: str = "Acme Global", slug: str = "acme-global") -> Tenant:
        return Tenant.create(name=name, slug=slug)

    @staticmethod
    def random() -> Tenant:
        suffix = uuid.uuid4().hex[:6]
        return Tenant.create(
            name=f"Enterprise {suffix}",
            slug=f"ent-{suffix}",
            admin_email=f"admin_{suffix}@enterprise.com",
        )


class RegisterTenantCommandMother:
    @staticmethod
    def create(
        tenant_name: str = "Acme Global",
        tenant_slug: str = "acme-global",
        admin_email: str = "admin@acme.com",
        admin_password: str = "SecurePassword123!",
        admin_full_name: str = "Admin Leader",
    ) -> RegisterTenantCommand:
        return RegisterTenantCommand(
            tenant_name=tenant_name,
            tenant_slug=tenant_slug,
            admin_email=admin_email,
            admin_password=admin_password,
            admin_full_name=admin_full_name,
        )

    @staticmethod
    def random() -> RegisterTenantCommand:
        suffix = uuid.uuid4().hex[:6]
        return RegisterTenantCommand(
            tenant_name=f"Company {suffix}",
            tenant_slug=f"comp-{suffix}",
            admin_email=f"ceo_{suffix}@company.com",
            admin_password="SuperPassword123!",
            admin_full_name=f"Leader {suffix}",
        )
