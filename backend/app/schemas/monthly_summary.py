from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date, time
from typing import Optional

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

    shift: Optional[ShiftSimpleResponse]

    model_config = ConfigDict(from_attributes=True)