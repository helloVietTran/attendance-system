from sqlalchemy import Column, Integer, Time, Date, ForeignKey, String, Enum, Text, DateTime, func
import enum

from app.db.session import Base

class RequestStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class AttendanceCorrection(Base):
    __tablename__ = "attendance_corrections"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    work_date = Column(Date, nullable=False)
    
    # Giờ mà nhân viên muốn sửa lại
    requested_check_in = Column(Time, nullable=True)
    requested_check_out = Column(Time, nullable=True)
    
    reason = Column(Text, nullable=False) # "Quên quẹt thẻ", "Máy hỏng"...
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING)
    
    approved_by = Column(Integer, ForeignKey("employees.id"), nullable=True) # ID người duyệt
    created_at = Column(DateTime, server_default=func.now())