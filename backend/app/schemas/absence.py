from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class AbsenceBase(BaseModel):
    absence_type_id: int
    start_date: date
    end_date: date
    reason: Optional[str] = None

class AbsenceCreate(AbsenceBase):
    user_id: int

class AbsenceResponse(AbsenceBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True