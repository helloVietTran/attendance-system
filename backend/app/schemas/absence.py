from pydantic import BaseModel, Field,field_validator
from datetime import date, datetime
from typing import Optional
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

class LongTermAbsenceCreate(BaseModel):
    employee_id: int
    absence_type_id: int
    start_date: date
    end_date: date
    reason: Optional[str] = "Nghỉ dài hạn theo chế độ (Admin tạo)"

    @field_validator('end_date')
    def check_duration(cls, v, info):
        if 'start_date' in info.data:
            start = info.data['start_date']
            duration = (v - start).days
            if duration < 30:
                raise ValueError("Kỳ nghỉ dài hạn phải có thời gian trên 30 ngày.")
        return v