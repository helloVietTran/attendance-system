from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

from app.db.session import Base

class ApprovalStatus(enum.Enum):

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class AbsenceType(Base):
    __tablename__ = "absence_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # Ví dụ: Sickness, Parental, Vacation
    code = Column(String(20), unique=True, nullable=False)  # Ví dụ: SICK, PARENT, VAC
    is_paid = Column(Integer, default=1)  # 1: Có lương, 0: Không lương

class Absence(Base):
    __tablename__ = "absences"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, index=True, nullable=False)
    absence_type_id = Column(Integer, ForeignKey("absence_types.id"), nullable=False)
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    type_info = relationship("AbsenceType")