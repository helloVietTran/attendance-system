from fastapi import APIRouter, Depends, Query
from typing import Dict
from sqlalchemy.orm import Session

from app.models.employee import UserRole
from app.core.dependencies import role_required
from app.schemas.base import ResponseSchema
from app.schemas.timesheet_period_control import TimesheetPeriodResponse
from app.db.session import get_db
from app.services.payroll_service import payroll_service

router = APIRouter(prefix="/payroll", tags=["Payroll Management"])

@router.post("/lock-period", response_model=ResponseSchema[TimesheetPeriodResponse])
def lock_timesheet(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020),
    closing_day: int = Query(20, description="Ngày chốt công hàng tháng"),
    db: Session = Depends(get_db),
    current_user=Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):

    result = payroll_service.lock_timesheet_period(
            db=db,
            admin_id=current_user["id"],
            month=month,
            year=year,
            closing_day=closing_day
    )
    return ResponseSchema(data=result)

@router.post(
    "/calculate-batch", 
    response_model=ResponseSchema[Dict],
    summary="Tính toán bảng công hàng tháng cho toàn bộ nhân viên",
    dependencies=[Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))],
)
def calculate_batch_payroll(
    closing_day: int = Query(20, ge=1, le=28, description="Ngày chốt công hàng tháng"),
    db: Session = Depends(get_db),
):

    result = payroll_service.calculate_all_employees_payroll(db, closing_day)
    return ResponseSchema(data=result)