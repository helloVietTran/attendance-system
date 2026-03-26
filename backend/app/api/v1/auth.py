from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db.session import get_db
from app.models.employee import Employee
from app.schemas.auth import LoginSchema
from app.schemas.employee import EmployeeRead

router = APIRouter(prefix="/auth", tags=["Authentication"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# hệ thống này dùng để tích hợp nên không hashe password
@router.post("/login", response_model=EmployeeRead)
async def login(data: LoginSchema, request: Request, db: Session = Depends(get_db)):
    user = db.query(Employee).filter(Employee.email == data.email).first()
    # if not user or not pwd_context.verify(data.password, user.password_hash):
    if not user or not data.password == user.password_hash:
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")

    request.session["user_id"] = user.id
    request.session["role"] = user.role
    request.session["email"] = user.email

    return user

@router.post("/logout")
async def logout(request: Request):
    
    request.session.clear()
    return {"message": "Đã đăng xuất"}

