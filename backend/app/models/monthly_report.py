from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime, func
from sqlalchemy.orm import relationship
from app.db.session import Base

class MonthlyWorkReport(Base):
    """
    Bảng lưu trữ tổng hợp công công hàng tháng sau khi HR chốt công.
    Dùng để tính lương (Payroll).
    """
    __tablename__ = "monthly_work_reports"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Khoảng thời gian chốt công (Ví dụ: 2026-02-01 đến 2026-02-31)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Các chỉ số tổng hợp (Đơn vị: Phút)
    work_minutes = Column(Integer, default=0)       # Tổng phút làm việc thực tế + bù trừ
    lack_minutes = Column(Integer, default=0)       # Tổng phút thiếu hụt

    estimated_minutes = Column(Integer, default=0)  # Số phút tạm tính cho các ngày chưa làm
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Quan hệ
    employee = relationship("Employee", backref="monthly_reports")