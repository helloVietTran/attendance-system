from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional

from app.models.absence import ApprovalStatus, AbsenceType

class AbsenceBase(BaseModel):
    absence_type: AbsenceType = Field(..., description="Loại nghỉ: annual, wedding, funeral, paternity")
    start_date: date
    end_date: date
    reason: Optional[str] = Field(None, max_length=500, json_schema_extra={"example": "Nghỉ kết hôn"})

    @field_validator('end_date')
    def check_dates(cls, v, info):
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError("Ngày kết thúc không được trước ngày bắt đầu")
        return v

class AbsenceCreate(AbsenceBase):
    pass

class AbsenceApprove(BaseModel):
    status: Optional[ApprovalStatus] = None
    reason: Optional[str] = None

class AbsenceResponse(BaseModel):
    id: int
    employee_id: int
    absence_type: AbsenceType
    start_date: date
    end_date: date
    status: ApprovalStatus
    reason: Optional[str]
    actual_days: int
    paid_days: int
    unpaid_days: int
    special_paid_days: int
    created_at: datetime

class LongTermAbsenceCreate(BaseModel):
    employee_id: int
    absence_type: AbsenceType
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