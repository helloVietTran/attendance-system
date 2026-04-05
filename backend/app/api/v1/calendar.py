from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.vacation import VacationCreate, VacationUpdate, VacationResponse
from app.schemas.work_compensation import WorkCompensationCreate, WorkCompensationUpdate, WorkCompensationResponse
from app.schemas.base import ResponseSchema
from app.services.calendar_service import calendar_service
from app.core.dependency import role_required
from app.models.employee import UserRole

router = APIRouter(prefix="/calendar", tags=["Lịch làm việc"])

@router.post(
    "/vacations", 
    response_model=ResponseSchema[VacationResponse],
    summary="Tạo mới ngày nghỉ lễ",
    description="Thêm một ngày lễ mới vào hệ thống. Có thể là nghỉ lễ định kỳ hàng năm hoặc nghỉ đột xuất.",
)
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

@router.get(
    "/vacations", 
    response_model=ResponseSchema[List[VacationResponse]],
    summary="Danh sách ngày nghỉ lễ",
    description="Lấy danh sách tất cả các ngày nghỉ lễ không phân trang."
)
def read_vacations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    result = calendar_service.get_vacations(db, skip=skip, limit=limit)
    return ResponseSchema(data=result)

@router.get("/vacations/{vacation_id}", response_model=ResponseSchema[VacationResponse])
def read_vacation(vacation_id: int, db: Session = Depends(get_db)):
    return ResponseSchema(data=calendar_service.get_vacation_by_id(db, vacation_id=vacation_id))

@router.post(
    "/compensations", 
    response_model=ResponseSchema[WorkCompensationResponse],
    summary="Tạo ngày làm bù",
    description="Chỉ định một ngày nghỉ (Thứ 7/CN) trở thành ngày làm việc bình thường."
)
def create_compensation(
    obj_in: WorkCompensationCreate, 
    db: Session = Depends(get_db),
    _ = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    return ResponseSchema(data=calendar_service.create_compensation(db, obj_in))

@router.put("/compensations/{comp_id}", response_model=ResponseSchema[WorkCompensationResponse])
def update_compensation(
    comp_id: int, 
    obj_in: WorkCompensationUpdate, 
    db: Session = Depends(get_db),
    _ = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    return ResponseSchema(data=calendar_service.update_compensation(db, comp_id, obj_in))

@router.delete("/compensations/{comp_id}")
def delete_compensation(
    comp_id: int, 
    db: Session = Depends(get_db),
    _ = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    return calendar_service.delete_compensation(db, comp_id)

@router.get("/compensations", response_model=ResponseSchema[List[WorkCompensationResponse]])
def read_compensations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    result = calendar_service.get_compensations(db, skip=skip, limit=limit)
    return ResponseSchema(data=result)