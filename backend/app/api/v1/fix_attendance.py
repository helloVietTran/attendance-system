from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.fix_attendance_service import fix_attendance_service
from app.schemas.attendance_correction import CorrectionCreate, CorrectionResponse
from app.schemas.base import ResponseSchema

router = APIRouter(prefix="/fix-requests", tags=["Attendance Corrections"])

@router.post("/", response_model=ResponseSchema[CorrectionResponse])
def request_fix_attendance(
    obj_in: CorrectionCreate, 
    db: Session = Depends(get_db),
    emp_id: int = 1 # Lấy từ Token
):
    result = fix_attendance_service.create_correction_request(db, emp_id, obj_in)
    return ResponseSchema(data=result)

@router.post("/{correction_id}/approve", response_model=ResponseSchema[CorrectionResponse])
def approve_fix(correction_id: int, db: Session = Depends(get_db), admin_id: int = 99):
    result = fix_attendance_service.approve_correction(db, correction_id, admin_id)
    return ResponseSchema(data=result)