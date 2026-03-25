from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.vacation import VacationCreate, VacationUpdate, VacationResponse
from app.schemas.absence import AbsenceApprove, AbsenceCreate, AbsenceResponse
from app.services.calendar_service import CalendarService

router = APIRouter(prefix="/calendar", tags=["Calendar"])

@router.post("/vacations", response_model=VacationResponse)
def create_vacation(obj_in: VacationCreate, db: Session = Depends(get_db)):
    return CalendarService.create_vacation(db, obj_in)

@router.put("/vacations/{vacation_id}", response_model=VacationResponse)
def update_vacation(vacation_id: int, obj_in: VacationUpdate, db: Session = Depends(get_db)):
    return CalendarService.update_vacation(db, vacation_id, obj_in)

@router.delete("/vacations/{vacation_id}")
def delete_vacation(vacation_id: int, db: Session = Depends(get_db)):
    return CalendarService.delete_vacation(db, vacation_id)

@router.get("/vacations", response_model=List[VacationResponse])
def read_vacations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return CalendarService.get_vacations(db, skip=skip, limit=limit)

@router.get("/vacations/{vacation_id}", response_model=VacationResponse)
def read_vacation(vacation_id: int, db: Session = Depends(get_db)):
    db_vacation = CalendarService.get_vacation_by_id(db, vacation_id=vacation_id)
    if db_vacation is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy ngày nghỉ này")
    return db_vacation

@router.post("/absences", response_model=AbsenceResponse)
def create_employee_absence(obj_in: AbsenceCreate, db: Session = Depends(get_db)):
    return CalendarService.create_absence(db, obj_in)

# lấy danh sách ngày nghỉ của 1 nhân viên
@router.get("/employees/{employee_id}/absences", response_model=List[AbsenceResponse])
def read_employee_absences(employee_id: int, db: Session = Depends(get_db)):
    return CalendarService.get_absences_by_employee(db, employee_id=employee_id)

# TODO: security
@router.delete("/absences/{absence_id}")
def cancel_absence(absence_id: int, db: Session = Depends(get_db)):
    return CalendarService.delete_pending_absence(db, absence_id=absence_id)

@router.patch("/absences/{absence_id}/approve", response_model=AbsenceResponse)
def approve_absence(
    absence_id: int, 
    obj_in: AbsenceApprove, 
    db: Session = Depends(get_db)
):
    return CalendarService.approve_absence(db, absence_id=absence_id, obj_in=obj_in)