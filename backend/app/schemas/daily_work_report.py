from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional

class WorkReportBase(BaseModel):
    employee_id: int
    work_date: date
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    late_arrive_minutes: int = 0
    leave_early_minutes: int = 0
    lack_minutes: int = 0
    overtime_minutes: int = 0
    in_office_minutes: int = 0
    work_time_minutes: int = 0

class WorkReportUpdate(WorkReportBase):
    pass

class WorkReportResponse(WorkReportBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True