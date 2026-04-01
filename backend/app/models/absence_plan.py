from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, Enum, Text, func
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.absence import AbsenceType, ApprovalStatus

class AbsencePlan(Base):
    __tablename__ = "absence_plans"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    
    # Khoảng thời gian nghỉ của kế hoạch này
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    
    absence_type = Column(Enum(AbsenceType), nullable=False)
    
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    
    approved_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Ghi chú lý do nghỉ hoặc ghi chú của người duyệt
    reason = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Quan hệ
    employee = relationship("Employee", foreign_keys=[employee_id], backref="absence_plans")
    approver = relationship("Employee", foreign_keys=[approved_by])