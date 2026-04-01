from sqlalchemy import Column, ForeignKey, Integer, String, Date, DECIMAL, Enum
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base

class UserRole(str, enum.Enum):
    EMPLOYEE = "employee"
    HR = "hr"
    ADMIN = "admin"

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
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE, nullable=False)

    # quan hệ
    absences = relationship("Absence", back_populates="employee")
    shift = relationship("Shift")

