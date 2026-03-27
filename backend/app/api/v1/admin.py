from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import role_required
from app.models.employee import UserRole
from app.schemas.base import ResponseSchema
from app.schemas.absence import LongTermAbsenceCreate, AbsenceResponse, AbsenceApprove

from app.services.absence_service import absence_service

router = APIRouter(
    prefix="/admin",
    tags=["Admin API"],
    dependencies=[Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))]
)

@router.post("/absences/long-term", response_model=ResponseSchema[AbsenceResponse])
def create_maternity_or_sick_leave(
    obj_in: LongTermAbsenceCreate,
    db: Session = Depends(get_db)
):
    # current_user = Depends(get_current_user) 
    result = absence_service.create_long_term_absence(db, obj_in)
    return ResponseSchema(data=result)

@router.patch("/absences/{absence_id}", response_model=ResponseSchema[AbsenceResponse])
def approve_absence(absence_id: int, obj_in: AbsenceApprove, db: Session = Depends(get_db)):
    result = absence_service.approve_absence(db, absence_id=absence_id, obj_in=obj_in)
    return ResponseSchema(data=result)