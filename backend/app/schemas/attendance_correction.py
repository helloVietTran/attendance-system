from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional

from app.models.absence import ApprovalStatus

class CorrectionCreate(BaseModel):
    work_date: date
    requested_check_in: Optional[time] = None
    requested_check_out: Optional[time] = None
    reason: str

class CorrectionResponse(BaseModel):
    id: int
    employee_id: int
    work_date: date
    status: ApprovalStatus
    reason: str
    created_at: datetime

    class Config:
        from_attributes = True