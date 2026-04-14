
from sqlalchemy import Column, Integer, DateTime, Date, String, Time, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.session import Base

class DailyWorkReport(Base):
    __tablename__ = "daily_work_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Thông tin ngày và giờ thực tế
    work_date = Column(Date, nullable=False, index=True)
    check_in = Column(Time, nullable=True)  # Giờ vào thực tế
    check_out = Column(Time, nullable=True) # Giờ ra thực tế

    late_arrive_minutes = Column(Integer, default=0) # Đi muộn
    leave_early_minutes = Column(Integer, default=0) # Về sớm
    lack_minutes = Column(Integer, default=0)        # Thiếu hụt (so với 8 tiếng)
    overtime_minutes = Column(Integer, default=0)    # Làm thêm
    in_office_minutes = Column(Integer, default=0)   # Tổng thời gian có mặt tại VP
    work_time_minutes = Column(Integer, default=0)   # Thời gian làm việc thực tế được tính công

    updated_at = Column(DateTime(6), server_default=func.now(), onupdate=func.now())
    note = Column(String(255), nullable=True)  # Ghi chú thêm nếu cần như nghỉ thai sản

    # Quan hệ
    employee = relationship("Employee")