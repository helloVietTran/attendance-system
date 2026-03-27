from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.shift_service import shift_service
from app.schemas.shift_change_request import ShiftChangeCreate, ShiftChangeResponse
from app.core.dependencies import get_current_user
from app.schemas.base import ResponseSchema

router = APIRouter(prefix="/shift-requests", tags=["Shift Requests"])

@router.post("/", response_model=ResponseSchema[ShiftChangeResponse])
def create_new_request(
    obj_in: ShiftChangeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return ResponseSchema(data= shift_service.create_request(db, current_user["id"], obj_in))
