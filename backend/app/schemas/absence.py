from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from enum import Enum

from app.models.absence import ApprovalStatus

class AbsenceTypeResponse(BaseModel):
    id: int
    name: str
    code: str
    is_paid: int
    class Config: from_attributes = True

class AbsenceBase(BaseModel):
    employee_id: int
    absence_type_id: int
    start_date: date
    end_date: date
    reason: Optional[str] = Field(None, example="Nghỉ ốm đi khám bệnh")

class AbsenceCreate(AbsenceBase):
    pass

class AbsenceUpdate(BaseModel):
    status: Optional[ApprovalStatus] = None
    reason: Optional[str] = None

class AbsenceResponse(AbsenceBase):
    id: int
    status: ApprovalStatus
    created_at: datetime
    type_info: Optional[AbsenceTypeResponse] = None 

    class Config:
        from_attributes = True

class AbsenceApprove(BaseModel):
    status: ApprovalStatus = Field(..., example="approved") # Chỉ nhận "approved" hoặc "rejected"
    note: Optional[str] = Field(None, example="Đã duyệt, chúc bạn nghỉ lễ vui vẻ")