from pydantic import BaseModel
from enum import Enum
from typing import Optional

class SystemSettingKey(str, Enum):
    LUNCH_START = "lunch_break_start"
    LUNCH_END = "lunch_break_end"
    ANNUAL_LEAVE = "annual_paid_leave_days"
    MATERNITY_LEAVE = "maternity_leave_months"
    MAX_CORRECTION = "max_attendance_correction_per_month"

class SystemSettingUpdate(BaseModel):
    key: SystemSettingKey
    value: str

class SystemSettingResponse(BaseModel):
    key: SystemSettingKey
    value: str
    description: Optional[str]

    class Config:
        from_attributes = True