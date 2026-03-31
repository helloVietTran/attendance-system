from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.vacation import VacationCreate, VacationUpdate, VacationResponse
from app.schemas.base import ResponseSchema
from app.services.calendar_service import calendar_service
from app.core.dependency import role_required
from app.models.employee import UserRole

router = APIRouter(prefix="/calendar", tags=["Calendar"])

@router.post("/vacations", response_model=ResponseSchema[VacationResponse])
def create_vacation(
    obj_in: VacationCreate, 
    db: Session = Depends(get_db),
    _ = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    return ResponseSchema(data=calendar_service.create_vacation(db, obj_in))

@router.put("/vacations/{vacation_id}", response_model=ResponseSchema[VacationResponse])
def update_vacation(
    vacation_id: int, 
    obj_in: VacationUpdate, 
    db: Session = Depends(get_db),
    _ = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    return ResponseSchema(data=calendar_service.update_vacation(db, vacation_id, obj_in))

@router.delete("/vacations/{vacation_id}")
def delete_vacation(
    vacation_id: int, 
    db: Session = Depends(get_db),
    _ = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    return calendar_service.delete_vacation(db, vacation_id)

@router.get("/vacations", response_model=ResponseSchema[List[VacationResponse]])
def read_vacations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    result = calendar_service.get_vacations(db, skip=skip, limit=limit)
    return ResponseSchema(data=result)

@router.get("/vacations/{vacation_id}", response_model=ResponseSchema[VacationResponse])
def read_vacation(vacation_id: int, db: Session = Depends(get_db)):
    return ResponseSchema(data=calendar_service.get_vacation_by_id(db, vacation_id=vacation_id))