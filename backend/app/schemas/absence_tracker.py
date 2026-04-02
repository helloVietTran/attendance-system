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