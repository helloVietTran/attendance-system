from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.employee_service import employee_service
from app.schemas.employee import EmployeeWithShiftResponse

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("/{employee_id}/shift", response_model=EmployeeWithShiftResponse)
def read_employee_shift_info(employee_id: int, db: Session = Depends(get_db)):
    """
    API lấy thông tin cơ bản của nhân viên và chi tiết ca làm việc hiện tại
    """
    return employee_service.get_employee_with_shift(db, employee_id)