import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.contexts.iam.presentation.router import get_tenant_repo, get_user_repo
from src.contexts.workforce.presentation.router import get_employee_repo
from tests.acceptance.test_iam_acceptance import InMemoryTenantRepo, InMemoryUserRepo
from tests.acceptance.test_workforce_acceptance import InMemoryEmployeeRepo


@pytest.fixture
def override_dependencies():
    tenant_repo = InMemoryTenantRepo()
    user_repo = InMemoryUserRepo()
    employee_repo = InMemoryEmployeeRepo()

    app.dependency_overrides[get_tenant_repo] = lambda: tenant_repo
    app.dependency_overrides[get_user_repo] = lambda: user_repo
    app.dependency_overrides[get_employee_repo] = lambda: employee_repo

    yield {
        "tenant_repo": tenant_repo,
        "user_repo": user_repo,
        "employee_repo": employee_repo,
    }

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_e2e_full_tenant_and_employee_lifecycle(override_dependencies):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        health_res = await client.get("/health")
        assert health_res.status_code == 200
        assert health_res.json()["architecture"] == "Screaming DDD"

        # 2. Register Tenant A
        reg_payload = {
            "tenant_name": "Acme Industries",
            "tenant_slug": "acme-ind",
            "admin_email": "admin@acme.com",
            "admin_password": "StrongPassword123!",
            "admin_full_name": "Alice Admin",
        }
        reg_res = await client.post("/api/v1/auth/register-tenant", json=reg_payload)
        assert reg_res.status_code == 201
        token = reg_res.json()["access_token"]
        assert token is not None

        headers = {"Authorization": f"Bearer {token}"}

        # 3. Create Employee in Tenant A
        emp_payload = {
            "first_name": "Lionel",
            "last_name": "Messi",
            "document_id": "ARG-101010",
            "department": "Operaciones",
            "position": "Capitán",
            "badge_code": "GOAT-10",
        }
        create_emp_res = await client.post("/api/v1/employees", json=emp_payload, headers=headers)
        assert create_emp_res.status_code == 201
        emp_data = create_emp_res.json()
        assert emp_data["full_name"] == "Lionel Messi"
        assert emp_data["badge_code"] == "GOAT-10"
        emp_id = emp_data["id"]

        # 4. List Employees
        list_res = await client.get("/api/v1/employees?search=Messi", headers=headers)
        assert list_res.status_code == 200
        list_data = list_res.json()
        assert list_data["total"] == 1
        assert list_data["items"][0]["id"] == emp_id

        # 5. Get Employee Detail
        detail_res = await client.get(f"/api/v1/employees/{emp_id}", headers=headers)
        assert detail_res.status_code == 200
        assert detail_res.json()["document_id"] == "ARG-101010"

        # 6. Update Employee Profile
        update_payload = {
            "position": "Líder de Operaciones",
            "department": "Dirección General",
        }
        update_res = await client.put(f"/api/v1/employees/{emp_id}", json=update_payload, headers=headers)
        assert update_res.status_code == 200
        assert update_res.json()["position"] == "Líder de Operaciones"

        # 7. Delete Employee
        del_res = await client.delete(f"/api/v1/employees/{emp_id}", headers=headers)
        assert del_res.status_code == 204
