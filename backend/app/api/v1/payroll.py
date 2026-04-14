from fastapi import APIRouter, Depends, Query
from typing import Dict,Optional
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from datetime import datetime

from app.models.employee import UserRole
from app.core.dependency import role_required
from app.db.session import get_db
from app.services.payroll_service import payroll_service
from app.schemas.base import ResponseSchema, PaginationResponse
from app.schemas.timesheet_period_control import TimesheetPeriodResponse
from app.schemas.payroll import PayrollCalculateRequest, MonthlyWorkReportResponse

router = APIRouter(prefix="/payroll", tags=["QL chốt công"])

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

@router.get(
    "/period-control", 
    response_model=ResponseSchema[Optional[TimesheetPeriodResponse]],
    summary="Lấy thông tin cấu hình kỳ chốt công theo tháng/năm"
)
def get_period_control(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020),
    db: Session = Depends(get_db),
    _ = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value, UserRole.EMPLOYEE.value]))
):
    result = payroll_service.get_timesheet_period(
        db=db,
        month=month,
        year=year
    )
    return ResponseSchema(data=result)

@router.post(
    "/calculate-batch", 
    response_model=ResponseSchema[Dict],
    summary="Tính toán bảng công hàng tháng cho toàn bộ nhân viên",
    dependencies=[Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))],
)
def calculate_batch_payroll(
    request_data: PayrollCalculateRequest,
    db: Session = Depends(get_db),
):
    result = payroll_service.calculate_all_employees_payroll(
        db, 
        closing_day=request_data.closing_day,
        month=request_data.month,
        year=request_data.year
    )
    
    return ResponseSchema(data=result)


@router.get(
    "/monthly-reports", 
    response_model=PaginationResponse[MonthlyWorkReportResponse],
    summary="Lấy danh sách công số tổng hợp hàng tháng"
)
def get_monthly_reports(
    employee_name: Optional[str] = Query(None, description="Tìm kiếm theo tên nhân viên"),
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1),
    db: Session = Depends(get_db),
    _ = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    result = payroll_service.get_monthly_reports(
        db=db,
        page=page,
        limit=limit,
        employee_name=employee_name
    )
    return PaginationResponse(
        data=result["data"],
        pagination=result["pagination"]
    )
    
@router.get("/export-excel", summary="Tải bảng công file Excel")
def export_payroll(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    db: Session = Depends(get_db),
    _ = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    current_month = month or datetime.now().month
    current_year = year or datetime.now().year
    
    file_stream, file_name = payroll_service.export_payroll_excel(db, current_month, current_year)
    
    return StreamingResponse(
        iter([file_stream.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={file_name}"
        }
    )