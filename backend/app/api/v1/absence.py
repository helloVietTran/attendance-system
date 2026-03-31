from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.services.absence_service import absence_service
from app.schemas.absence import AbsenceCreate, AbsenceResponse
from app.schemas.base import ResponseSchema
from app.core.dependency import get_current_user

router = APIRouter(prefix="/absences", tags=["Absence"])

@router.get("/employees/{employee_id}/absences", response_model=ResponseSchema[List[AbsenceResponse]])
def read_employee_absences(employee_id: int, db: Session = Depends(get_db)):
    return ResponseSchema(data=absence_service.get_absences_by_employee(db, employee_id=employee_id))

@router.post("/", response_model=ResponseSchema[AbsenceResponse])
def create_absence(
    obj_in: AbsenceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user) 
):
    return ResponseSchema(data=absence_service.create_absence(db, obj_in, current_user["id"]))

@router.delete("/{absence_id}")
def cancel_absence(
    absence_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return absence_service.delete_pending_absence(db, absence_id=absence_id, empId=current_user["id"])