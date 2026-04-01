from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependency import role_required, get_current_user
from app.models.employee import UserRole
from app.schemas.base import ResponseSchema
from app.schemas.attendance_correction import CorrectionResponse
from app.schemas.shift_change_request import ShiftChangeResponse

from app.services.fix_attendance_service import fix_attendance_service
from app.services.shift_service import shift_service
from app.schemas.overtime_request import OvertimeApprove, OvertimeResponse
from app.services.overtime_service import overtime_service

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))]
)

@router.put("/fix-requests/{fix_id}/approve", response_model=ResponseSchema[CorrectionResponse])
def approve_fix_request(fix_id: int, db: Session = Depends(get_db)):
    current_user = Depends(get_current_user)

    result = fix_attendance_service.approve_fix_request(db, fix_id, admin_id=current_user["id"])
    return ResponseSchema(data=result)

@router.post("/shift/{request_id}/approve", response_model=ResponseSchema[ShiftChangeResponse])
def approve_shift_change(
    request_id: int,
    db: Session = Depends(get_db),
    admin_id: int = 99
):
    return ResponseSchema(data=shift_service.approve_request(db, request_id, admin_id))

@router.patch("/overtimes/{ot_id}/approve", response_model=ResponseSchema[OvertimeResponse])
def approve_overtime_request(
    ot_id: int,
    obj_in: OvertimeApprove,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_user) 
):
    """Admin duyệt hoặc từ chối đơn OT"""
    result = overtime_service.approve_request(
        db, 
        ot_id=ot_id, 
        admin_id=current_admin["id"], 
        obj_in=obj_in
    )
    return ResponseSchema(data=result)