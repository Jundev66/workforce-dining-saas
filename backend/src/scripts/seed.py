import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.database import AsyncSessionLocal
from src.shared.infrastructure.security import hash_password
from src.contexts.iam.infrastructure.persistence.models import TenantModel, UserModel
from src.contexts.workforce.infrastructure.persistence.models import EmployeeModel
from src.contexts.dining.infrastructure.persistence.models import MealRecordModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


DEMO_TENANT_ID = "11111111-1111-4111-a111-111111111111"
DEMO_TENANT_SLUG = "acme-foods"
DEMO_TENANT_NAME = "Acme Industrial Foods S.A."

DEMO_ADMIN_ID = "22222222-2222-4222-a222-222222222222"
DEMO_ADMIN_EMAIL = "admin@acme.com"
DEMO_PASSWORD = "Password123!"


async def seed_database() -> None:
    print("🌱 Starting SaaS database seeder...")

    async with AsyncSessionLocal() as session:
        # 1. Establish tenant context for RLS in this session
        await session.execute(
            text("SELECT set_config('app.current_tenant_id', :tenant_id, false)"),
            {"tenant_id": DEMO_TENANT_ID},
        )

        # 2. Check if demo tenant already exists
        result = await session.execute(
            select(TenantModel).where(TenantModel.slug == DEMO_TENANT_SLUG)
        )
        tenant = result.scalar_one_or_none()

        if not tenant:
            tenant = TenantModel(
                id=DEMO_TENANT_ID,
                name=DEMO_TENANT_NAME,
                slug=DEMO_TENANT_SLUG,
                is_active=True,
                created_at=utc_now(),
                updated_at=utc_now(),
            )
            session.add(tenant)
            await session.flush()
            print(f"  ✓ Tenant created: {tenant.name} (slug: {tenant.slug})")
        else:
            print(f"  ℹ Tenant already exists: {tenant.name}")

        # 3. Create Admin User
        user_res = await session.execute(
            select(UserModel).where(
                UserModel.tenant_id == DEMO_TENANT_ID,
                UserModel.email == DEMO_ADMIN_EMAIL,
            )
        )
        admin_user = user_res.scalar_one_or_none()

        if not admin_user:
            admin_user = UserModel(
                id=DEMO_ADMIN_ID,
                tenant_id=DEMO_TENANT_ID,
                email=DEMO_ADMIN_EMAIL,
                hashed_password=hash_password(DEMO_PASSWORD),
                full_name="Carlos Rodriguez (Admin)",
                role="admin",
                is_active=True,
                created_at=utc_now(),
                updated_at=utc_now(),
            )
            session.add(admin_user)
            await session.flush()
            print(f"  ✓ Admin user created: {admin_user.email} / {DEMO_PASSWORD}")
        else:
            print(f"  ℹ Admin user already exists: {admin_user.email}")

        # 4. Create Workforce Employees
        employees_data = [
            {
                "id": "33333333-3333-4333-a333-333333333301",
                "first_name": "Carlos",
                "last_name": "Gomez",
                "document_id": "DNI-10203040",
                "email": "carlos.chef@acme.com",
                "department": "Cocina Central",
                "position": "Chef Ejecutivo",
                "badge_code": "CHEF-001",
            },
            {
                "id": "33333333-3333-4333-a333-333333333302",
                "first_name": "Maria",
                "last_name": "Fernandez",
                "document_id": "DNI-20304050",
                "email": "maria.fernandez@acme.com",
                "department": "Operaciones",
                "position": "Operaria de Planta",
                "badge_code": "OP-101",
            },
            {
                "id": "33333333-3333-4333-a333-333333333303",
                "first_name": "Esteban",
                "last_name": "Quito",
                "document_id": "DNI-30405060",
                "email": "esteban.log@acme.com",
                "department": "Logística",
                "position": "Encargado de Depósito",
                "badge_code": "LOG-202",
            },
            {
                "id": "33333333-3333-4333-a333-333333333304",
                "first_name": "Sofia",
                "last_name": "Rossi",
                "document_id": "DNI-40506070",
                "email": "sofia.rossi@acme.com",
                "department": "Mantenimiento",
                "position": "Técnica Electromecánica",
                "badge_code": "MNT-303",
            },
            {
                "id": "33333333-3333-4333-a333-333333333305",
                "first_name": "Gonzalo",
                "last_name": "Higuain",
                "document_id": "DNI-50607080",
                "email": "gonzalo.sec@acme.com",
                "department": "Seguridad",
                "position": "Vigilante de Turno",
                "badge_code": "SEC-404",
            },
        ]

        created_employees = {}
        for emp_info in employees_data:
            emp_res = await session.execute(
                select(EmployeeModel).where(
                    EmployeeModel.tenant_id == DEMO_TENANT_ID,
                    EmployeeModel.document_id == emp_info["document_id"],
                )
            )
            existing_emp = emp_res.scalar_one_or_none()
            if not existing_emp:
                new_emp = EmployeeModel(
                    id=emp_info["id"],
                    tenant_id=DEMO_TENANT_ID,
                    first_name=emp_info["first_name"],
                    last_name=emp_info["last_name"],
                    document_id=emp_info["document_id"],
                    email=emp_info["email"],
                    department=emp_info["department"],
                    position=emp_info["position"],
                    status="active",
                    badge_code=emp_info["badge_code"],
                    created_at=utc_now(),
                    updated_at=utc_now(),
                )
                session.add(new_emp)
                created_employees[emp_info["badge_code"]] = emp_info["id"]
                print(f"  ✓ Employee created: {new_emp.first_name} {new_emp.last_name} (Badge: {new_emp.badge_code})")
            else:
                created_employees[emp_info["badge_code"]] = existing_emp.id

        await session.flush()

        # 5. Create Sample Today's Meal Records (for live metrics)
        # We record lunch for OP-101 and LOG-202 so the dashboard shows activity
        sample_scans = [
            ("OP-101", "lunch", "Ingreso regular turno mañana"),
            ("LOG-202", "lunch", "Ración autorizada comedor 1"),
        ]

        for badge, meal_type, notes in sample_scans:
            emp_id = created_employees.get(badge)
            if emp_id:
                # Check if already scanned today
                scan_res = await session.execute(
                    select(MealRecordModel).where(
                        MealRecordModel.tenant_id == DEMO_TENANT_ID,
                        MealRecordModel.employee_id == emp_id,
                        MealRecordModel.meal_type == meal_type,
                    )
                )
                if not scan_res.scalar_one_or_none():
                    record = MealRecordModel(
                        id=str(uuid.uuid4()),
                        tenant_id=DEMO_TENANT_ID,
                        employee_id=emp_id,
                        meal_type=meal_type,
                        badge_code=badge,
                        status="approved",
                        notes=notes,
                        consumed_at=utc_now(),
                    )
                    session.add(record)
                    print(f"  ✓ Sample meal record created: Badge {badge} ({meal_type})")

        await session.commit()

    print("\n🎉 Database seeded successfully!")
    print("-------------------------------------------------------------")
    print(f" Organization / Slug : {DEMO_TENANT_SLUG}")
    print(f" Admin Login Email   : {DEMO_ADMIN_EMAIL}")
    print(f" Admin Password      : {DEMO_PASSWORD}")
    print(" Badges Ready to Test:")
    print("   • CHEF-001 (Carlos Gomez - Not scanned yet today)")
    print("   • OP-101   (Maria Fernandez - Already scanned lunch today -> Test duplicate!)")
    print("   • MNT-303  (Sofia Rossi - Not scanned yet today)")
    print("-------------------------------------------------------------\n")


if __name__ == "__main__":
    asyncio.run(seed_database())
