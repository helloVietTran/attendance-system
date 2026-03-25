from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.shift_service import shift_service
from app.schemas.shift_change_request import ShiftChangeCreate, ShiftChangeResponse

router = APIRouter(prefix="/shift-requests", tags=["Shift Requests"])

@router.post("/", response_model=ShiftChangeResponse)
def create_new_request(
    obj_in: ShiftChangeCreate, 
    db: Session = Depends(get_db),
    current_user_id: int = 1 
):
    return shift_service.create_request(db, current_user_id, obj_in)

@router.post("/{request_id}/approve", response_model=ShiftChangeResponse)
def approve_shift_change(
    request_id: int, 
    db: Session = Depends(get_db),
    admin_id: int = 99 # lấy từ session
):
    return shift_service.approve_request(db, request_id, admin_id)