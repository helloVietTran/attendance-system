from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependency import get_current_user, role_required
from app.db.session import get_db
from app.services.fix_attendance_service import fix_attendance_service
from app.schemas.attendance_correction import CorrectionCreate, CorrectionResponse
from app.schemas.base import ResponseSchema
from app.models.employee import UserRole

router = APIRouter(prefix="/fix-attendance-requests", tags=["Yêu cầu sửa công"])

@router.post("/", response_model=ResponseSchema[CorrectionResponse])
def request_fix_attendance(
    obj_in: CorrectionCreate, 
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    result = fix_attendance_service.create_correction_request(db, current_user["id"], obj_in)
    return ResponseSchema(data=result)

@router.get("/my-requests", response_model=ResponseSchema[List[CorrectionResponse]])
def get_my_fix_attendance(
    month: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user_id = current_user["id"]
    
    result = fix_attendance_service.get_my_corrections(
        db, 
        employee_id=user_id, 
        month=month, 
        year=year
    )
    return ResponseSchema(data=result)

@router.put("/{fix_id}/approve", response_model=ResponseSchema[CorrectionResponse])
def approve_fix_request(
    fix_id: int, 
    db: Session = Depends(get_db),
    current_admin = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    result = fix_attendance_service.approve_fix_request(db, fix_id, admin_id=current_admin["id"])
    return ResponseSchema(data=result)
