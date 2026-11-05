from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.presentation.api.dependencies import get_current_user, get_employee_repository
from src.presentation.schemas.employee_schemas import (
    EmployeeCreateRequest,
    EmployeeUpdateRequest,
    EmployeeResponse,
    EmployeeListResponse,
)
from src.infrastructure.persistence.repositories.sqlalchemy_employee_repository import SQLAlchemyEmployeeRepository
from src.application.use_cases.employee_use_cases import (
    CreateEmployeeUseCase,
    CreateEmployeeCommand,
    ListEmployeesUseCase,
    GetEmployeeDetailUseCase,
    UpdateEmployeeUseCase,
    UpdateEmployeeCommand,
    DeleteEmployeeUseCase,
)
from src.domain.models.employee import EmployeeStatus

router = APIRouter(prefix="/employees", tags=["Employee Management"])


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    data: EmployeeCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    employee_repo: SQLAlchemyEmployeeRepository = Depends(get_employee_repository),
):
    tenant_id = current_user["tenant_id"]
    use_case = CreateEmployeeUseCase(employee_repo)
    try:
        employee = await use_case.execute(
            CreateEmployeeCommand(
                tenant_id=tenant_id,
                first_name=data.first_name,
                last_name=data.last_name,
                document_id=data.document_id,
                email=str(data.email) if data.email else None,
                phone=data.phone,
                department=data.department,
                position=data.position,
                badge_code=data.badge_code,
            )
        )
        return employee
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=EmployeeListResponse)
async def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    department: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    employee_repo: SQLAlchemyEmployeeRepository = Depends(get_employee_repository),
):
    status_enum = None
    if status_filter:
        try:
            status_enum = EmployeeStatus(status_filter.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status value. Must be one of: {[s.value for s in EmployeeStatus]}",
            )

    use_case = ListEmployeesUseCase(employee_repo)
    items, total = await use_case.execute(
        skip=skip,
        limit=limit,
        department=department,
        status=status_enum,
        search=search,
    )

    return EmployeeListResponse(
        items=[EmployeeResponse(**emp.__dict__, full_name=emp.full_name) for emp in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee_detail(
    employee_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    employee_repo: SQLAlchemyEmployeeRepository = Depends(get_employee_repository),
):
    use_case = GetEmployeeDetailUseCase(employee_repo)
    try:
        employee = await use_case.execute(employee_id)
        return EmployeeResponse(**employee.__dict__, full_name=employee.full_name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: str,
    data: EmployeeUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    employee_repo: SQLAlchemyEmployeeRepository = Depends(get_employee_repository),
):
    status_enum = None
    if data.status:
        try:
            status_enum = EmployeeStatus(data.status.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status value. Must be one of: {[s.value for s in EmployeeStatus]}",
            )

    use_case = UpdateEmployeeUseCase(employee_repo)
    try:
        employee = await use_case.execute(
            UpdateEmployeeCommand(
                employee_id=employee_id,
                first_name=data.first_name,
                last_name=data.last_name,
                email=str(data.email) if data.email else None,
                phone=data.phone,
                department=data.department,
                position=data.position,
                status=status_enum,
            )
        )
        return EmployeeResponse(**employee.__dict__, full_name=employee.full_name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    employee_repo: SQLAlchemyEmployeeRepository = Depends(get_employee_repository),
):
    use_case = DeleteEmployeeUseCase(employee_repo)
    try:
        await use_case.execute(employee_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
