from pydantic import BaseModel
from datetime import date, time
from typing import Optional

class AttendanceLogBase(BaseModel):
    employee_id: int
    log_date: date
    shift_start: time
    shift_end: time
    checked_time: time
    check_type: Optional[str] = "IN"

class AttendanceLogCreate(AttendanceLogBase):
    pass

class AttendanceLogResponse(AttendanceLogBase):
    id: int
    # Chúng ta có thể dùng Pydantic để lấy Name/Email từ quan hệ Employee
    # employee_name: str 
    # email: str

    class Config:
        from_attributes = True