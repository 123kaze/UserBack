from pydantic import BaseModel
from typing import Optional
from datetime import datetime,date

class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True # 允许从 ORM 对象直接转换

class PositionBase(BaseModel):
    title: str
    description: Optional[str] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None

class PositionCreate(PositionBase):
    pass

class PositionResponse(PositionBase):
    id: int

    class Config:
        from_attributes = True

class EmployeeBase(BaseModel):
    name: str
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    department_id: Optional[int] = None
    position_id: Optional[int] = None
    birth_date: Optional[date] = None
    hire_date: Optional[date] = None
    salary: Optional[float] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int

    class Config:
        from_attributes = True
