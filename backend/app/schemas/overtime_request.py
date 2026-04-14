from pydantic import BaseModel, Field, ConfigDict
from datetime import date, time, datetime
from typing import Optional
from app.models.overtime_request import OTType
from app.models.absence import ApprovalStatus

class OvertimeBase(BaseModel):
    work_date: date
    start_time: time
    end_time: time
    ot_type: OTType = OTType.NORMAL_DAY
    reason: Optional[str] = Field(None, max_length=255)

class OvertimeCreate(OvertimeBase):
    """Dùng cho nhân viên tự đăng ký"""
    pass

class OvertimeUpdate(BaseModel):
    """Dùng để cập nhật đơn nếu chưa duyệt"""
    work_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    reason: Optional[str] = None

class OvertimeApprove(BaseModel):
    status: ApprovalStatus # APPROVED hoặc REJECTED

class OvertimeResponse(BaseModel):
    id: int
    work_date: date
    start_time: time
    end_time: time
    actual_work_time: Optional[int] = None
    ot_type: OTType
    multiplier: float
    status: ApprovalStatus
    reason: Optional[str] = None
    created_at: datetime
    employee_name: Optional[str] = None
    employee_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)