from pydantic import BaseModel
from datetime import date, time

class AttendanceCreate(BaseModel):
    employee_id: int
    log_date: date
    shift_start: time
    shift_end: time
    checked_time: time

class AttendanceResponse(AttendanceCreate):
    id: int
    class Config:
        from_attributes = True