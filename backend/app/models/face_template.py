from sqlalchemy import Column, Integer, ForeignKey, JSON, DateTime, String, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class FaceTemplate(Base):
    __tablename__ = "face_templates"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    
    face_encoding = Column(JSON, nullable=False) 
    
    model_name = Column(String(50), default="buffalo_s") 
    
    created_at = Column(DateTime, server_default=func.now())
    
    employee = relationship("Employee", backref="face_template")