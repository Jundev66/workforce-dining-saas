from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.database import get_db_session
from src.shared.infrastructure.security import decode_access_token
from src.shared.infrastructure.tenant_context import set_current_tenant_id
from src.contexts.workforce.domain.value_objects import EmployeeStatus
from src.contexts.workforce.infrastructure.persistence.repositories import SQLAlchemyEmployeeRepository
from src.contexts.workforce.application.use_cases import (
    CreateEmployeeUseCase,
    ListEmployeesUseCase,
    GetEmployeeDetailUseCase,
    UpdateEmployeeUseCase,
    DeleteEmployeeUseCase,
)
from src.contexts.workforce.application.dtos import (
    CreateEmployeeCommand,
    UpdateEmployeeCommand,
    EmployeeDTO,
    PaginatedEmployeesDTO,
)

router = APIRouter(prefix="/employees", tags=["Workforce - Employee Management"])
security_scheme = HTTPBearer(auto_error=True)


class EmployeeCreateRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    document_id: str = Field(..., min_length=3, max_length=50)
    department: str = Field(default="General", max_length=100)
    position: str = Field(default="Employee", max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    badge_code: Optional[str] = Field(default=None, max_length=100)


class EmployeeUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    department: Optional[str] = Field(default=None, max_length=100)
    position: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    status: Optional[str] = None


def get_employee_repo(db: AsyncSession = Depends(get_db_session)) -> SQLAlchemyEmployeeRepository:
    return SQLAlchemyEmployeeRepository(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> Dict[str, Any]:
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing tenant context",
        )
    set_current_tenant_id(tenant_id)
    return payload


@router.post("", response_model=EmployeeDTO, status_code=status.HTTP_201_CREATED)
async def create_employee(
    data: EmployeeCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: SQLAlchemyEmployeeRepository = Depends(get_employee_repo),
):
    use_case = CreateEmployeeUseCase(repo)
    try:
        return await use_case.execute(
            CreateEmployeeCommand(
                tenant_id=current_user["tenant_id"],
                first_name=data.first_name,
                last_name=data.last_name,
                document_id=data.document_id,
                department=data.department,
                position=data.position,
                email=str(data.email) if data.email else None,
                phone=data.phone,
                badge_code=data.badge_code,
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=PaginatedEmployeesDTO)
async def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    department: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: SQLAlchemyEmployeeRepository = Depends(get_employee_repo),
):
    status_enum = None
    if status_filter:
        try:
            status_enum = EmployeeStatus(status_filter.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of {[s.value for s in EmployeeStatus]}",
            )
    use_case = ListEmployeesUseCase(repo)
    return await use_case.execute(
        skip=skip,
        limit=limit,
        department=department,
        status=status_enum,
        search=search,
    )


@router.get("/{employee_id}", response_model=EmployeeDTO)
async def get_employee_detail(
    employee_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: SQLAlchemyEmployeeRepository = Depends(get_employee_repo),
):
    use_case = GetEmployeeDetailUseCase(repo)
    try:
        return await use_case.execute(employee_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{employee_id}", response_model=EmployeeDTO)
async def update_employee(
    employee_id: str,
    data: EmployeeUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: SQLAlchemyEmployeeRepository = Depends(get_employee_repo),
):
    status_enum = None
    if data.status:
        try:
            status_enum = EmployeeStatus(data.status.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of {[s.value for s in EmployeeStatus]}",
            )
    use_case = UpdateEmployeeUseCase(repo)
    try:
        return await use_case.execute(
            UpdateEmployeeCommand(
                employee_id=employee_id,
                first_name=data.first_name,
                last_name=data.last_name,
                department=data.department,
                position=data.position,
                email=str(data.email) if data.email else None,
                phone=data.phone,
                status=status_enum,
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: SQLAlchemyEmployeeRepository = Depends(get_employee_repo),
):
    use_case = DeleteEmployeeUseCase(repo)
    try:
        await use_case.execute(employee_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
