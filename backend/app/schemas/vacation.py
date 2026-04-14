from pydantic import BaseModel, ConfigDict, Field
from datetime import date
from typing import Optional

from app.models.vacation import VacationType

class VacationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, json_schema_extra={"example": "Nghỉ Tết Nguyên Đán"})
    description: Optional[str] = Field(None, max_length=500, json_schema_extra={"example": "Nghỉ theo quy định nhà nước"})
    start_date: date
    end_date: date
    vacation_type: VacationType = Field(default=VacationType.HOLIDAY)
    is_paid: bool = Field(default=True)
    is_recurring: bool = Field(default=True)

class VacationCreate(VacationBase):
    pass

class VacationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    vacation_type: Optional[VacationType] = None
    is_paid: Optional[bool] = None
    is_recurring: Optional[bool] = None

class VacationResponse(VacationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)