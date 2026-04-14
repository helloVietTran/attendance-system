from pydantic import BaseModel, Field, field_serializer, field_validator, ConfigDict
from datetime import date, datetime
from typing import Any, Optional

from app.models.absence import ApprovalStatus, AbsenceType

class AbsencePlanCreate(BaseModel):
    absence_type: AbsenceType = Field(
        ...,
        description="Loại nghỉ: annual, wedding, funeral, maternity, paternity"
    )
    start_date: date = Field(..., json_schema_extra={"example": "2026-04-10"})
    end_date: date = Field(..., json_schema_extra={"example": "2026-04-12"})
    reason: Optional[str] = Field(
        None, 
        max_length=500, 
        description="Lý do xin nghỉ phép",
        json_schema_extra={"example": "Nghỉ về quê có việc gia đình"}
    )

    @field_validator('end_date')
    def check_dates(cls, v, info):
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError("Ngày kết thúc không được trước ngày bắt đầu")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "absence_type": "annual",
                "start_date": "2026-04-15",
                "end_date": "2026-04-17",
                "reason": "Nghỉ phép năm đi du lịch"
            }
        }
    )

class AbsencePlanApprove(BaseModel):
    status: Optional[ApprovalStatus] = Field(
        None, 
        description="Trạng thái phê duyệt: 'approved' (Đồng ý) hoặc 'rejected' (Từ chối)"
    )
    reason: Optional[str] = None

class AbsencePlanResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: Optional[str] = None  # Trường này sẽ được gán thủ công trong service
    start_date: date
    end_date: date
    status: ApprovalStatus
    reason: Optional[str]
    created_at: datetime
    absence_type: Any
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_serializer('absence_type')
    def serialize_absence_type(self, absence_type):
        # Nếu absence_type là Enum Member, lấy giá trị phần tử đầu tiên của tuple
        if isinstance(absence_type.value, tuple):
            return absence_type.value[0]
        return absence_type.value
    
class AbsenceResponse(BaseModel):
    id: int
    employee_id: int
    work_date: date
    is_paid: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
