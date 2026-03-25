from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func

from app.db.session import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    title = Column(String(100), nullable=False) # "Chúc mừng sinh nhật! 🎂"
    content = Column(String(255), nullable=False) # "Bạn được tặng 1 ngày công quà tặng cho ngày hôm nay."
    
    is_read = Column(Boolean, default=False)
    notification_type = Column(String(20)) # "BIRTHDAY", "SHIFT_CHANGE", "SYSTEM"
    
    created_at = Column(DateTime, server_default=func.now())