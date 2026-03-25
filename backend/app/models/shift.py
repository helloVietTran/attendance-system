from sqlalchemy import Column, Integer, String, Time, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship

from app.db.session import Base

class Shift(Base):
    """Bảng định nghĩa các loại ca làm việc trong công ty"""
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False) # Ví dụ: "Ca Hành Chính", "Ca Sáng", "Ca Đêm"
    
    start_time = Column(Time, nullable=False)   # 08:00:00
    end_time = Column(Time, nullable=False)     # 17:00:00
    
    # Số công tương ứng (Ví dụ: 1 công, 0.5 công)
    work_value = Column(Integer, default=1) 
    
    is_active = Column(Boolean, default=True)

class EmployeeShift(Base):
    """Bảng phân ca cụ thể: Nhân viên A làm ca X vào ngày Y"""
    __tablename__ = "employee_shifts"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    
    work_date = Column(Date, nullable=False, index=True) # Ngày làm việc cụ thể
    
    # Quan hệ
    employee = relationship("Employee")
    shift = relationship("Shift")