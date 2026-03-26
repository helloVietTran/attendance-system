from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.services.absence_service import absence_service 
from app.schemas.absence import AbsenceApprove, AbsenceCreate, AbsenceResponse, LongTermAbsenceCreate

router = APIRouter(prefix="/absences", tags=["Absence"])

@router.get("/employees/{employee_id}/absences", response_model=List[AbsenceResponse])
def read_employee_absences(employee_id: int, db: Session = Depends(get_db)):
    return absence_service.get_absences_by_employee(db, employee_id=employee_id)

@router.post("/long-term")
def create_maternity_or_sick_leave(
    obj_in: LongTermAbsenceCreate,
    db: Session = Depends(get_db),
    admin_id = 1
):
    """
    API dành cho Admin: Đăng ký nghỉ thai sản/dài hạn cho nhân viên.
    """
    return absence_service.create_long_term_absence(
        db, obj_in, admin_id=admin_id
    )

@router.post("/", response_model=AbsenceResponse)
def create_employee_absence(obj_in: AbsenceCreate, db: Session = Depends(get_db)):
    return absence_service.create_absence(db, obj_in)


@router.delete("/{absence_id}")
def cancel_absence(absence_id: int, db: Session = Depends(get_db)):
    return absence_service.delete_pending_absence(db, absence_id=absence_id)

@router.patch("/{absence_id}/approve", response_model=AbsenceResponse)
def approve_absence(absence_id: int, obj_in: AbsenceApprove, db: Session = Depends(get_db)):
    return absence_service.approve_absence(db, absence_id=absence_id, obj_in=obj_in)