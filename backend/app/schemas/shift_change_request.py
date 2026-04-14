from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.shift_change_request import RequestStatus

class ShiftChangeCreate(BaseModel):
    new_shift_id: int
    current_shift_id: int
    reason: Optional[str] = None

class ShiftChangeResponse(BaseModel):
    id: int
    employee_id: int
    target_month: int
    target_year: int
    old_shift_id: int
    new_shift_id: int
    status: RequestStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)