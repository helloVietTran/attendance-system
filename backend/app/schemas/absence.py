from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import date, datetime
from typing import Optional

from app.models.absence import ApprovalStatus, AbsenceType

class AbsencePlanCreate(BaseModel):
    absence_type: AbsenceType = Field(
        ...,
        description="Loại nghỉ: annual, wedding, funeral, maternity, paternity"
    )
    start_date: date = Field(..., example="2026-04-10")
    end_date: date = Field(..., example="2026-04-12")
    reason: Optional[str] = Field(
        None, 
        max_length=500, 
        description="Lý do xin nghỉ phép",
        example="Nghỉ về quê có việc gia đình"
    )

    @field_validator('end_date')
    def check_dates(cls, v, info):
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError("Ngày kết thúc không được trước ngày bắt đầu")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "absence_type": "annual",
                "start_date": "2026-04-15",
                "end_date": "2026-04-17",
                "reason": "Nghỉ phép năm đi du lịch"
            }
        }

class AbsencePlanApprove(BaseModel):
    status: Optional[ApprovalStatus] = Field(
        None, 
        description="Trạng thái phê duyệt: 'approved' (Đồng ý) hoặc 'rejected' (Từ chối)"
    )
    reason: Optional[str] = None

class AbsencePlanResponse(BaseModel):
    id: int
    employee_id: int
    start_date: date
    end_date: date
    status: ApprovalStatus
    reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
    
class AbsenceResponse(BaseModel):
    id: int
    employee_id: int
    work_date: date
    is_paid: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
