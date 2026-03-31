import enum
from sqlalchemy import Column, DateTime, Integer, Time, Date, Enum, ForeignKey, Text, Float, func
from sqlalchemy.orm import relationship

from app.models.absence import ApprovalStatus
from app.db.session import Base

class OTType(str, enum.Enum):
    NORMAL_DAY = "normal_day"
    WEEKEND_DAY = "weekend_day"
    HOLIDAY_DAY = "holiday_day"

    @property
    def multiplier(self) -> float:
        """Trả về hệ số lương tương ứng với từng loại OT"""
        mapping = {
            OTType.NORMAL_DAY: 1.5,
            OTType.WEEKEND_DAY: 2.0,
            OTType.HOLIDAY_DAY: 3.0,
        }
        return mapping.get(self, 1.0)

class OvertimeRequest(Base):
    """Đơn đăng ký làm thêm giờ"""
    __tablename__ = "overtime_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    work_date = Column(Date, nullable=False, index=True)

    actual_work_time = Column(Integer, nullable=False) # số phút làm thêm
    
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    ot_type = Column(Enum(OTType), default=OTType.NORMAL_DAY, nullable=False)
    
    multiplier = Column(Float, default=1.5)

    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    reason = Column(Text, nullable=True)

    approved_by = Column(Integer, ForeignKey("employees.id"), nullable=True) # ID của Manager/HR
    approved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Quan hệ
    employee = relationship("Employee", foreign_keys=[employee_id])
    approver = relationship("Employee", foreign_keys=[approved_by])