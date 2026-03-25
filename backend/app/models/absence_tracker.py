from sqlalchemy import Boolean, Column, Integer, DateTime, Date, func
from sqlalchemy.orm import relationship

from app.db.session import Base

class AbsenceTracker(Base):
    """Theo dõi trạng thái vắng mặt liên tục của nhân viên"""
    __tablename__ = "absence_trackers"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, unique=True, nullable=False, index=True)
    
    # Số ngày nghỉ liên tiếp tính đến hiện tại
    consecutive_days_off = Column(Integer, default=0)
    
    # Ngày cuối cùng họ có mặt (Check-in)
    last_present_date = Column(Date, nullable=True)
    
    # Đánh dấu nếu đã gửi cảnh báo cho HR (để tránh gửi spam mỗi ngày)
    has_alerted_hr = Column(Boolean, default=False)
    
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())