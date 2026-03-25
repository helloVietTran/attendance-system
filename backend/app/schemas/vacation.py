from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

# Schema chung
class VacationBase(BaseModel):
    title: str = Field(..., example="Kỷ niệm 10 năm thành lập công ty")
    description: Optional[str] = None
    start_date: date
    end_date: date
    is_recurring: bool = False
    deduct_from_allowance: bool = False

# Dùng khi tạo mới (POST)
class VacationCreate(VacationBase):
    pass

# Dùng khi cập nhật (PATCH/PUT)
class VacationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_recurring: Optional[bool] = None
    deduct_from_allowance: Optional[bool] = None

# Dùng khi trả về dữ liệu (Response)
class VacationResponse(VacationBase):
    id: int

    class Config:
        from_attributes = True