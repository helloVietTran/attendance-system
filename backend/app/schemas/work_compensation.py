from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class WorkCompensationBase(BaseModel):
    title: str
    compensate_date: date
    description: Optional[str] = None

class WorkCompensationCreate(WorkCompensationBase):
    pass

class WorkCompensationUpdate(BaseModel):
    title: Optional[str] = None
    compensate_date: Optional[date] = None
    description: Optional[str] = None

class WorkCompensationResponse(WorkCompensationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)