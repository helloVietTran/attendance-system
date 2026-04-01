from pydantic import BaseModel
from datetime import date
from typing import Optional

class AbsenceAlertResponse(BaseModel):
    employee_id: int
    employee_name: str
    consecutive_days_off: int
    last_present_date: Optional[date]
    is_unexcused: bool

    class Config:
        from_attributes = True