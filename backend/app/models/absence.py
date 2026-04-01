from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum, Text, func
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base

class ApprovalStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class AbsenceType(enum.Enum):
    ANNUAL = ("annual", "Nghỉ phép năm", -1, False) # -1 nghĩa là trừ vào 14 ngày phép có lương
    MATERNITY = ("maternity", "Nghỉ thai sản", 180, True)
    WEDDING = ("wedding", "Nghỉ kết hôn", 3, True)
    FUNERAL = ("funeral", "Nghỉ tang chế", 3, True)
    PATERNITY = ("paternity", "Nghỉ vợ sinh", 3, True)

    def __init__(self, code, label, max_days, is_paid):
        self.code = code
        self.label = label
        self.max_days = max_days
        self.is_paid = is_paid
    
    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.code == value or member.name.lower() == str(value).lower():
                return member
        return None

class Absence(Base):
    __tablename__ = "absences"

    id = Column(Integer, primary_key=True, index=True)
    absence_type = Column(Enum(AbsenceType), default=AbsenceType.ANNUAL)
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    actual_days = Column(Integer, nullable=False)  # Tổng ngày nghỉ thực tế (đã trừ T7, CN, Lễ)
    paid_days = Column(Integer, default=0)  
    unpaid_days = Column(Integer, default=0)
    special_paid_days = Column(Integer, default=0)

    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    employee = relationship("Employee", back_populates="absences")