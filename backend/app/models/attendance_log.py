from sqlalchemy import Column, Integer, func, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    log_date = Column(Date, nullable=False, default=func.now())
    
    shift_start = Column(Time, nullable=False) # Ví dụ: 08:00:00
    shift_end = Column(Time, nullable=False)   # Ví dụ: 17:00:00
    
    checked_time = Column(Time, nullable=False)
    
    employee = relationship("Employee")