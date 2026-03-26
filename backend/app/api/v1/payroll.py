from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Dict
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.payroll_service import payroll_service

router = APIRouter(prefix="/payroll", tags=["Payroll Management"])

@router.post("/lock-period")
def lock_timesheet(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020),
    closing_day: int = Query(20, description="Ngày chốt công hàng tháng"),
    db: Session = Depends(get_db),
    admin_id=99
):

    return payroll_service.lock_timesheet_period(
            db=db,
            admin_id=admin_id,
            month=month,
            year=year,
            closing_day=closing_day
    )

@router.post(
    "/calculate-batch", 
    response_model=Dict,
    status_code=status.HTTP_200_OK,
    summary="Tính toán bảng công hàng tháng cho toàn bộ nhân viên"
)
def calculate_batch_payroll(
    closing_day: int = Query(20, ge=1, le=28, description="Ngày chốt công hàng tháng"),
    db: Session = Depends(get_db),
    admin_id = 99
):

    try:
        result = payroll_service.calculate_all_employees_payroll(db, closing_day)
        return result
        
    except Exception as e:
        print(f"Error in calculate_batch_payroll: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quá trình tính toán thất bại: {str(e)}"
        )