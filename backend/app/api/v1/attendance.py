from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime

from app.db.session import get_db
from app.services.attendance_service import attendance_service
from app.schemas.attendance_log import AttendanceResponse
from app.schemas.daily_work_report import DailyWorkReportResponse
from app.schemas.base import ResponseSchema
from app.core.dependency import get_current_user

router = APIRouter(prefix="/attendance", tags=["Chấm công & Báo cáo công"])

@router.get("/logs/{employee_id}", response_model=ResponseSchema[AttendanceResponse])
def get_attendance_logs_by_empId(
    employee_id: int,
    month: int = Query(..., ge=1, le=12),
    year: int = Query(default=datetime.now().year),
    db: Session = Depends(get_db)
):
    """Lấy log chấm công tháng của 1 nhân viên"""
    return ResponseSchema(data=attendance_service.get_attendance_logs_by_month(db, employee_id, month, year))

@router.post("/logs/calculate", response_model=ResponseSchema[DailyWorkReportResponse])
def calculate_work_day(
    target_date: date, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Tính toán dữ liệu công dựa trên Logs và Overtime request"""
    result = attendance_service.process_daily_attendance(db, employee_id=current_user["id"] ,work_date=target_date)

    return ResponseSchema(data=result)

@router.get("/daily-reports/{employee_id}", response_model=ResponseSchema[List[DailyWorkReportResponse]])
def get_daily_work_reports(
    employee_id: int,
    month: int = Query(..., ge=1, le=12, description="Tháng cần lấy báo cáo"),
    year: int = Query(default=datetime.now().year, description="Năm cần lấy báo cáo"),
    db: Session = Depends(get_db)
):
    """
    Lấy bảng công chi tiết của nhân viên trong tháng.
    Dữ liệu bao gồm: Giờ vào/ra, số phút đi muộn, về sớm, OT, v.v.
    """
    reports = attendance_service.get_daily_work_reports_by_month(db, employee_id, month, year)
    return ResponseSchema(data=reports)