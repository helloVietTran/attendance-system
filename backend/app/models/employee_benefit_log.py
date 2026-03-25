from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime, func
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base

class BenefitType(str, enum.Enum):
    BIRTHDAY = "birthday"
    SPECIAL_BONUS = "special_bonus"

class EmployeeBenefitLog(Base):
    """Lưu vết các loại công được tặng thêm hoặc phúc lợi đặc biệt"""
    __tablename__ = "employee_benefit_logs"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    benefit_type = Column(String(20), nullable=False) # Ví và: "BIRTHDAY"
    work_value = Column(Integer, default=480)          # Được cộng 1 công
    apply_date = Column(Date, nullable=False)         # Ngày áp dụng (Ngày sinh nhật)
    
    description = Column(String(255)) # "Chúc mừng sinh nhật nhân viên"
    created_at = Column(DateTime, server_default=func.now())

    employee = relationship("Employee")