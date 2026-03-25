from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from app.db.session import Base

class TimesheetMonthlySummary(Base):
    """Bảng chốt công hàng tháng (Chu kỳ 21 tháng trước -> 20 tháng này)"""
    __tablename__ = "timesheet_monthly_sums"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    month = Column(Integer, nullable=False) # Tháng tính lương (Tháng T)
    year = Column(Integer, nullable=False)  # Năm tính lương
    
    # Tổng hợp từ DailyWorkReport (21 tháng trước -> 20 tháng này)
    total_work_minutes = Column(Integer, default=0) # Tổng phút làm việc thực tế
    total_late_minutes = Column(Integer, default=0)
    total_overtime_minutes = Column(Integer, default=0)
    
    # TRƯỜNG QUAN TRỌNG: TRUY THU (Trừ công thiếu từ cuối tháng trước chuyển sang)
    deducted_minutes_from_last_month = Column(Integer, default=0) 

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())