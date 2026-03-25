from sqlalchemy import Column, Integer, ForeignKey, Enum, Text, DateTime, func
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base

class RequestStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ShiftChangeRequest(Base):
    __tablename__ = "shift_change_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Tháng và năm áp dụng ca mới
    target_month = Column(Integer, nullable=False) # Ví dụ: 4
    target_year = Column(Integer, nullable=False)  # Ví dụ: 2024
    
    # Ca cũ và Ca mới muốn đổi sang
    old_shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    new_shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING)
    reason = Column(Text, nullable=True)
    
    # Tracking thông tin HR xử lý
    processed_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    new_shift = relationship("Shift", foreign_keys=[new_shift_id])