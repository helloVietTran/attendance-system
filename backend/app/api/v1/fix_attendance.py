from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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
    emp_id: int = Depends(get_current_user)
):
    result = fix_attendance_service.create_correction_request(db, emp_id, obj_in)
    return ResponseSchema(data=result)

@router.put("/{fix_id}/approve", response_model=ResponseSchema[CorrectionResponse])
def approve_fix_request(
    fix_id: int, 
    db: Session = Depends(get_db),
    current_admin = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    result = fix_attendance_service.approve_fix_request(db, fix_id, admin_id=current_admin["id"])
    return ResponseSchema(data=result)
