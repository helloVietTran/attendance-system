from pydantic import BaseModel
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
    # Lồng thông tin ca làm vào đây
    shift: Optional[ShiftSimpleResponse]

    class Config:
        from_attributes = True