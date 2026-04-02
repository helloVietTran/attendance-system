from pydantic import BaseModel, ConfigDict
from datetime import date, time
from typing import Optional
from decimal import Decimal
from app.models.employee import UserRole

class EmployeeRead(BaseModel):
    id: int
    full_name: str
    age: int
    email: str
    department_id: int
    role: UserRole
    dob: date
    salary: Decimal
    shift_id: int

    model_config = ConfigDict(from_attributes=True)

class ShiftSimpleResponse(BaseModel):
    id: int
    name: str
    start_time: time
    end_time: time

    model_config = ConfigDict(from_attributes=True)

class EmployeeWithShiftResponse(BaseModel):
    id: int
    full_name: str
    email: str
    department_id: int
    # Lồng thông tin ca làm vào đây
    shift: Optional[ShiftSimpleResponse]

    model_config = ConfigDict(from_attributes=True)