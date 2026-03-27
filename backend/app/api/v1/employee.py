from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.employee_service import employee_service
from app.schemas.base import ResponseSchema
from app.schemas.employee import EmployeeWithShiftResponse

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("/{employee_id}", response_model=ResponseSchema[EmployeeWithShiftResponse])
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    return ResponseSchema(data=employee_service.get_employee_with_shift(db, employee_id))