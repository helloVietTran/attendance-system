from pydantic import BaseModel, EmailStr
from datetime import date, time
from typing import Optional

class ShiftSimpleResponse(BaseModel):
    id: int
    name: str
    start_time: time
    end_time: time

    class Config:
        from_attributes = True

class EmployeeWithShiftResponse(BaseModel):
    id: int
    full_name: str
    email: str
    department_id: int

    shift: Optional[ShiftSimpleResponse]

    class Config:
        from_attributes = True