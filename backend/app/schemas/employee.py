from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class EmployeeBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150, example="Nguyễn Văn A")
    age: int = Field(..., gt=18, lt=100, example=25) # Giả sử nhân viên phải > 18 tuổi
    email: EmailStr = Field(..., example="user@example.com")
    department_id: int = Field(..., example=1)

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int

    class Config:
        # Quan trọng: Dòng này cho phép Pydantic đọc dữ liệu từ SQLAlchemy Object
        from_attributes = True