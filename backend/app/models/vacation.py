from sqlalchemy import Column, Integer, String, Date, Boolean, Enum
import enum

from app.db.session import Base

class VacationType(enum.Enum):
    HOLIDAY = "holiday"        # Lễ tết (Tết, 30/4...)
    COMPANY_EVENT = "event"    # Sinh nhật công ty, Teambuilding
    EMERGENCY = "emergency"    # Đột xuất (Mưa bão, sự cố điện...)

class Vacation(Base):
    __tablename__ = "vacations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Trường quan trọng để phân loại
    vacation_type = Column(Enum(VacationType), default=VacationType.HOLIDAY)
    
    # Mặc định nghỉ đột xuất/lễ thường là có lương (không trừ phép)
    is_paid = Column(Boolean, default=True)

    is_recurring = Column(Boolean, default=True) # nghỉ thường niên