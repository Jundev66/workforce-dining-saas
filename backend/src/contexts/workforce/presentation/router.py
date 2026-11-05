from fastapi import APIRouter, status
from src.contexts.workforce.presentation.controllers.common import get_employee_repo, get_current_user
from src.contexts.workforce.application.dtos import EmployeeDTO, PaginatedEmployeesDTO
from src.contexts.workforce.presentation.controllers.create_employee_controller import (
    CreateEmployeeController,
)
from src.contexts.workforce.presentation.controllers.list_employees_controller import (
    ListEmployeesController,
)
from src.contexts.workforce.presentation.controllers.get_employee_detail_controller import (
    GetEmployeeDetailController,
)
from src.contexts.workforce.presentation.controllers.update_employee_controller import (
    UpdateEmployeeController,
)
from src.contexts.workforce.presentation.controllers.delete_employee_controller import (
    DeleteEmployeeController,
)

router = APIRouter(prefix="/employees", tags=["Workforce - Employee Management"])

# Register Single-Action Controller endpoints
router.add_api_route(
    "",
    CreateEmployeeController.handle,
    methods=["POST"],
    response_model=EmployeeDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Onboard new employee",
)

router.add_api_route(
    "",
    ListEmployeesController.handle,
    methods=["GET"],
    response_model=PaginatedEmployeesDTO,
    summary="List paginated employees",
)

router.add_api_route(
    "/{employee_id}",
    GetEmployeeDetailController.handle,
    methods=["GET"],
    response_model=EmployeeDTO,
    summary="Get employee profile",
)

router.add_api_route(
    "/{employee_id}",
    UpdateEmployeeController.handle,
    methods=["PUT"],
    response_model=EmployeeDTO,
    summary="Update employee profile",
)

router.add_api_route(
    "/{employee_id}",
    DeleteEmployeeController.handle,
    methods=["DELETE"],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete employee",
)

__all__ = ["router", "get_employee_repo", "get_current_user"]
