from sqlalchemy import Column, Integer, Date, String

from app.db.session import Base

class WorkCompensation(Base):
    """Bảng lưu các ngày làm bù (Thứ 7, CN được chỉ định đi làm)"""
    __tablename__ = "work_compensations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    compensate_date = Column(Date, nullable=False, unique=True, index=True)
    description = Column(String(500), nullable=True)