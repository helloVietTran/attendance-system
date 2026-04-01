from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.shift_service import shift_service
from app.schemas.shift_change_request import ShiftChangeCreate, ShiftChangeResponse
from app.core.dependency import get_current_user, role_required
from app.schemas.base import ResponseSchema
from app.models.employee import UserRole

router = APIRouter(prefix="/shift", tags=["Ca làm"])

@router.post("/shift-change-request", response_model=ResponseSchema[ShiftChangeResponse])
def create_new_request(
    obj_in: ShiftChangeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return ResponseSchema(data= shift_service.create_request(db, current_user["id"], obj_in))

@router.post("/shift-change-request/{request_id}/approve", response_model=ResponseSchema[ShiftChangeResponse])
def approve_shift_change(
    request_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    return ResponseSchema(data=shift_service.approve_request(db, request_id, current_admin["id"]))