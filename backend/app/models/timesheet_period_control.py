from sqlalchemy import Column, Date, Integer, String, Boolean, DateTime, ForeignKey, func

from app.db.session import Base

class TimesheetPeriodControl(Base):
    """Bảng kiểm soát trạng thái khóa công theo từng kỳ lương"""
    __tablename__ = "timesheet_period_controls"

    id = Column(Integer, primary_key=True, index=True)

    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    closing_date = Column(Date, nullable=False)
    
    # Trạng thái khóa
    is_locked = Column(Boolean, default=True)
    
    # Thông tin người thực hiện khóa (HR/Admin)
    locked_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    locked_at = Column(DateTime, nullable=True)
    
    note = Column(String(255), nullable=True)

    updated_at = Column(DateTime(6), server_default=func.now(), onupdate=func.now())