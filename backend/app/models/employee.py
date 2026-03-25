from sqlalchemy import Column, ForeignKey, Integer, String, Date, DECIMAL
from sqlalchemy.orm import relationship

from app.db.session import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(150), nullable=False)
    age = Column(Integer, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    department_id = Column(Integer, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    dob = Column(Date, nullable=False)
    salary = Column(DECIMAL(10, 2), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)

    # quan hệ
    absences = relationship("Absence", back_populates="employee")
    shift = relationship("Shift")

