import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.contexts.iam.presentation.router import get_tenant_repo, get_user_repo
from src.contexts.workforce.presentation.router import get_employee_repo
from tests.acceptance.test_iam_acceptance import InMemoryTenantRepo, InMemoryUserRepo
from tests.acceptance.test_workforce_acceptance import InMemoryEmployeeRepo


@pytest.fixture
def override_deps():
    tenant_repo = InMemoryTenantRepo()
    user_repo = InMemoryUserRepo()
    employee_repo = InMemoryEmployeeRepo()

    app.dependency_overrides[get_tenant_repo] = lambda: tenant_repo
    app.dependency_overrides[get_user_repo] = lambda: user_repo
    app.dependency_overrides[get_employee_repo] = lambda: employee_repo

    yield employee_repo
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_idempotent_duplicate_request_prevention(override_deps):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register tenant
        reg = await client.post("/api/v1/auth/register-tenant", json={
            "tenant_name": "Idempotent Corp",
            "tenant_slug": "idem-corp",
            "admin_email": "admin@idem.com",
            "admin_password": "Password123!",
            "admin_full_name": "Admin Idem",
        })
        token = reg.json()["access_token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Idempotency-Key": "unique-request-key-9999",
        }

        # 2. First submission
        payload = {
            "first_name": "Pedro",
            "last_name": "Pascal",
            "document_id": "DNI-777",
            "department": "IT",
            "position": "Lead",
        }
        res1 = await client.post("/api/v1/employees", json=payload, headers=headers)
        assert res1.status_code == 201
        data1 = res1.json()

        # 3. Double-click simulation with the exact same idempotency key
        res2 = await client.post("/api/v1/employees", json=payload, headers=headers)
        assert res2.status_code == 201
        assert res2.headers.get("x-cache-lookup") == "HIT-IDEMPOTENT"
        data2 = res2.json()

        # 4. Result must be identical without throwing duplicate errors
        assert data1["id"] == data2["id"]
        assert data1["document_id"] == data2["document_id"]
