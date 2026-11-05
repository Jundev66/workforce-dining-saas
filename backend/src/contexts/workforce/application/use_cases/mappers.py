from src.contexts.workforce.domain.entities import Employee
from src.contexts.workforce.application.dtos import EmployeeDTO


def to_employee_dto(emp: Employee) -> EmployeeDTO:
    return EmployeeDTO(
        id=emp.id,
        tenant_id=emp.tenant_id,
        first_name=emp.first_name,
        last_name=emp.last_name,
        full_name=emp.full_name,
        document_id=str(emp.document_id),
        department=str(emp.department),
        position=emp.position,
        status=emp.status.value,
        badge_code=str(emp.badge_code),
        email=emp.email,
        phone=emp.phone,
        created_at=emp.created_at,
        updated_at=emp.updated_at,
    )
