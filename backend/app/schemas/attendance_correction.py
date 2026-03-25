from pydantic import BaseModel, Field
from datetime import date, time, datetime
from typing import Optional
from enum import Enum

# Khai báo Enum trạng thái để đồng bộ với SQL
class RequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

# 1. Schema Cơ sở (Base)
class AttendanceCorrectionBase(BaseModel):
    work_date: date
    requested_check_in: Optional[time] = None
    requested_check_out: Optional[time] = None
    reason: str = Field(..., min_length=10, description="Lý do chỉnh sửa, tối thiểu 10 ký tự")

# 2. Schema khi Nhân viên gửi yêu cầu (Create)
class AttendanceCorrectionCreate(AttendanceCorrectionBase):
    employee_id: int # ID của nhân viên gửi yêu cầu

# 3. Schema khi Cấp trên phê duyệt (Approve/Reject)
class AttendanceCorrectionUpdate(BaseModel):
    status: RequestStatus
    approved_by: int # ID của người quản lý thực hiện duyệt
    admin_note: Optional[str] = None # Ghi chú thêm từ sếp (nếu có)

# 4. Schema trả về dữ liệu (Response)
class AttendanceCorrectionResponse(AttendanceCorrectionBase):
    id: int
    employee_id: int
    status: RequestStatus
    approved_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True # Cho phép chuyển đổi từ SQLAlchemy sang JSON