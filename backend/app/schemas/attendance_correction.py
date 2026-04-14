from pydantic import BaseModel, ConfigDict
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
    employee_name: Optional[str]
    work_date: date
    status: ApprovalStatus
    reason: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)