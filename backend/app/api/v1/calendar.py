from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.vacation import VacationCreate, VacationUpdate, VacationResponse
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