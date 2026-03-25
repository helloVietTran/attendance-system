from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

# chỉ được thay đổica của tháng tháng sau, không được thay đổi ca của tháng trước
class ShiftChangeRequestBase(BaseModel):
    target_month: int = Field(..., ge=1, le=12)
    target_year: int = Field(..., ge=2024)
    new_shift_id: int
    reason: Optional[str] = None

class ShiftChangeRequestCreate(ShiftChangeRequestBase):
    employee_id: int
    old_shift_id: int

class ShiftChangeRequestResponse(ShiftChangeRequestBase):
    id: int
    employee_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True