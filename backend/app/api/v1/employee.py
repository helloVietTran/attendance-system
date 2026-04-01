from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.employee_service import employee_service
from app.schemas.base import PaginationMetadata, PaginationResponse, ResponseSchema
from app.schemas.employee import EmployeeWithShiftResponse

router = APIRouter(prefix="/employees", tags=["Nhân viên"])

@router.get("/search", response_model=PaginationResponse[EmployeeWithShiftResponse])
def search_employees(
    keyword: Optional[str] = Query(None, description="Tìm theo tên, email hoặc ID"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    employees, pagination_data = employee_service.search_employees(
        db, keyword=keyword, page=page, limit=limit
    )
    
    return PaginationResponse(
        data=employees,
        pagination=PaginationMetadata(**pagination_data)
    )

@router.get("/{employee_id}", response_model=ResponseSchema[EmployeeWithShiftResponse])
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    return ResponseSchema(data=employee_service.get_employee_with_shift(db, employee_id))