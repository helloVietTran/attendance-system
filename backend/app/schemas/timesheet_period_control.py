from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional

class TimesheetPeriodControlResponse(BaseModel):
    id: int
    month: int
    year: int
    period_start_date: date
    period_end_date: date
    is_locked: bool
    locked_at: Optional[datetime] = None
    note: Optional[str] = None

    class Config:
        from_attributes = True

class LockTimesheetPeriodRequest(BaseModel):
    month: int
    year: int
    hr_id: int
    note: Optional[str] = None