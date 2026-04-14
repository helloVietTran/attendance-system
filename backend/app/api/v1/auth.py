

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.employee import Employee
from app.schemas.auth import LoginSchema
from app.schemas.base import ResponseSchema
from app.services.auth_service import create_access_token
from app.core.dependency import get_current_user

router = APIRouter(prefix="/auth", tags=["Xác thực & Phiên làm việc"])

@router.post("/login", response_model=ResponseSchema[dict])
async def login(data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(Employee).filter(Employee.email == data.email).first()

    if not user or not data.password == user.password_hash: # hệ thống tính công là hệ thống tích hợp nên không hash password
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")

    token = create_access_token({
        "user_id": user.id,
        "role": user.role,
        "email": user.email
    })

    return ResponseSchema(
        data={
            "access_token": token,
            "token_type": "bearer"
        }
    )

@router.get("/introspect", response_model=ResponseSchema[dict])
async def check_auth(_ = Depends(get_current_user)):
    return ResponseSchema(
        data= {
            "authenticated": True,
        }
    )
