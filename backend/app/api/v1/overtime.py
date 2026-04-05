from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependency import get_current_user, role_required
from app.schemas.base import ResponseSchema
from app.db.session import get_db
from app.schemas.overtime_request import OvertimeApprove, OvertimeCreate, OvertimeResponse
from app.services.overtime_service import overtime_service
from app.models.employee import UserRole

router = APIRouter(prefix="/overtimes", tags=["Quản lý làm thêm giờ"])

@router.post("/", response_model=ResponseSchema[OvertimeResponse])
def request_ot(
    obj_in: OvertimeCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = overtime_service.create_request(db, obj_in, current_user["id"])
    return ResponseSchema(data=result)

@router.delete("/{ot_id}")
def cancel_ot(
    ot_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    overtime_service.delete_pending_request(db, ot_id, current_user["id"])
    return ResponseSchema(message="Đã hủy đơn OT thành công")

@router.patch("/{ot_id}/approve", response_model=ResponseSchema[OvertimeResponse])
def approve_overtime_request(
    ot_id: int,
    obj_in: OvertimeApprove,
    db: Session = Depends(get_db),
    current_admin = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    """Admin duyệt hoặc từ chối đơn OT"""
    result = overtime_service.approve_request(
        db, 
        ot_id=ot_id, 
        admin_id=current_admin["id"], 
        obj_in=obj_in
    )
    return ResponseSchema(data=result)