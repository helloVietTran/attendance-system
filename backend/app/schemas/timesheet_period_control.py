from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional

class TimesheetPeriodBase(BaseModel):
    month: int = Field(..., ge=1, le=12, description="Tháng trong năm (1-12)")
    year: int = Field(..., ge=2000, description="Năm")
    closing_date: date
    is_locked: bool = True
    note: Optional[str] = Field(None, max_length=255)

class TimesheetPeriodResponse(TimesheetPeriodBase):
    """Dữ liệu trả về cho Client"""
    id: int
    locked_by: Optional[int] = None
    locked_at: Optional[datetime] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)