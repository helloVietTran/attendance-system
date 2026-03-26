from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.fix_attendance_service import fix_attendance_service
from app.schemas.attendance_correction import CorrectionCreate, CorrectionResponse

router = APIRouter(prefix="/fix-requests", tags=["Attendance Corrections"])

@router.post("/", response_model=CorrectionResponse)
def request_fix_attendance(
    obj_in: CorrectionCreate, 
    db: Session = Depends(get_db),
    emp_id: int = 1 # Lấy từ Token
):
    return fix_attendance_service.create_correction_request(db, emp_id, obj_in)

@router.post("/{correction_id}/approve")
def approve_fix(correction_id: int, db: Session = Depends(get_db), admin_id: int = 99):
    return fix_attendance_service.approve_correction(db, correction_id, admin_id)