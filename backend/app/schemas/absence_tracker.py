from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class AbsenceAlertResponse(BaseModel):
    employee_id: int
    employee_name: str
    consecutive_days_off: int
    last_present_date: Optional[date]
    is_unexcused: bool

    model_config = ConfigDict(from_attributes=True)
    
class AbsenceTrackerResponse(BaseModel):
    employee_id: int
    current_year_total: int
    current_year_used: int
    carried_over_from_last_year: int
    carried_over_used: int
    total_remaining: int
    class Config:
        from_attributes = True