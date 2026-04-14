from sqlalchemy import Boolean, Column, Integer, Date, DateTime, ForeignKey, Enum, Text, func
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base

class ApprovalStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class AbsenceType(enum.Enum):
    ANNUAL = ("annual", "Nghỉ phép năm", 0, False) # 0: tính vào quỹ nghỉ phép năm
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
    
    work_date = Column(Date, nullable=False)
    is_paid = Column(Boolean, default=False)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    employee = relationship("Employee", back_populates="absences")
    
    absence_type = Column(Enum(AbsenceType), index=True)