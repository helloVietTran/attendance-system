from sqlalchemy import Column, Integer, String, Text

from app.db.session import Base

class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True) # Tên cấu hình
    value = Column(Text, nullable=False) # Giá trị (Lưu dạng string, sau đó convert theo logic)
    description = Column(String(255), nullable=True) # Giải thích ý nghĩa cấu hình