from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class EmployeeCreateRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, examples=["Carlos"])
    last_name: str = Field(..., min_length=1, max_length=100, examples=["Perez"])
    document_id: str = Field(..., min_length=3, max_length=50, examples=["DOC-998234"])
    email: Optional[EmailStr] = Field(default=None, examples=["carlos.perez@company.com"])
    phone: Optional[str] = Field(default=None, max_length=50, examples=["+54 9 11 1234-5678"])
    department: str = Field(default="Operations", max_length=100, examples=["Operations"])
    position: str = Field(default="Operator", max_length=100, examples=["Operator"])
    badge_code: Optional[str] = Field(default=None, max_length=100, examples=["BADGE-001"])


class EmployeeUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    department: Optional[str] = Field(default=None, max_length=100)
    position: Optional[str] = Field(default=None, max_length=100)
    status: Optional[str] = Field(default=None, examples=["active", "inactive", "on_leave"])


class EmployeeResponse(BaseModel):
    id: str
    tenant_id: str
    first_name: str
    last_name: str
    full_name: str
    document_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    department: str
    position: str
    status: str
    badge_code: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EmployeeListResponse(BaseModel):
    items: List[EmployeeResponse]
    total: int
    skip: int
    limit: int
