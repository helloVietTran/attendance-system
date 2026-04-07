from pydantic import BaseModel, ConfigDict
from datetime import date, time

class AttendanceCreate(BaseModel):
    employee_id: int
    log_date: date
    shift_start: time
    shift_end: time
    checked_time: time

class AttendanceLogResponse(BaseModel):
    id: int
    employee_id: int
    log_date: date
    shift_start: time 
    shift_end: time
    checked_time: time

    model_config = ConfigDict(from_attributes=True)
