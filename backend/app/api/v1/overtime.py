from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.schemas.base import ResponseSchema
from app.db.session import get_db
from app.schemas.overtime_request import OvertimeCreate, OvertimeResponse
from app.services import overtime_service

router = APIRouter(prefix="/overtimes", tags=["Overtime Management"])

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