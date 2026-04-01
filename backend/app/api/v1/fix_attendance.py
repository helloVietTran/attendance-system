from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependency import get_current_user
from app.db.session import get_db
from app.services.fix_attendance_service import fix_attendance_service
from app.schemas.attendance_correction import CorrectionCreate, CorrectionResponse
from app.schemas.base import ResponseSchema

router = APIRouter(prefix="/fix-requests", tags=["Yêu cầu sửa công"])

@router.post("/", response_model=ResponseSchema[CorrectionResponse])
def request_fix_attendance(
    obj_in: CorrectionCreate, 
    db: Session = Depends(get_db),
    emp_id: int = Depends(get_current_user)
):
    result = fix_attendance_service.create_correction_request(db, emp_id, obj_in)
    return ResponseSchema(data=result)