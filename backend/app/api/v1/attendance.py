from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime

from app.db.session import get_db
from app.services.attendance_service import attendance_service
from app.schemas.attendance_log import AttendanceResponse, AttendanceCreate
from app.schemas.daily_work_report import DailyWorkReportResponse

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/log", response_model=AttendanceResponse)
def add_attendance_log(obj_in: AttendanceCreate, db: Session = Depends(get_db)):
    """API để máy chấm công hoặc app mobile gửi log về"""
    return attendance_service.ingest_log(db, obj_in)

@router.get("/report/{employee_id}", response_model=List[AttendanceResponse])
def get_monthly_report(
    employee_id: int,
    month: int = Query(..., ge=1, le=12),
    year: int = Query(default=datetime.now().year),
    db: Session = Depends(get_db)
):
    """Lấy log chấm công tháng của 1 nhân viên"""
    return attendance_service.get_attendance_by_month(db, employee_id, month, year)

# logic core
@router.post("/calculate/{employee_id}")
def calculate_work_day(employee_id: int, target_date: date, db: Session = Depends(get_db)):
    """Tính toán dữ liệu công dựa trên Logs và Settings Cache"""
    result = attendance_service.process_daily_attendance(db, employee_id, target_date)
    if not result:
        return {"message": "Không tìm thấy dữ liệu chấm công cho ngày này."}
    return result

@router.get("/monthly/{employee_id}", response_model=List[DailyWorkReportResponse])
def get_monthly_work_report(
    employee_id: int,
    month: int = Query(..., ge=1, le=12, description="Tháng cần lấy báo cáo"),
    year: int = Query(default=datetime.now().year, description="Năm cần lấy báo cáo"),
    db: Session = Depends(get_db)
):
    """
    Lấy bảng công chi tiết của nhân viên trong tháng.
    Dữ liệu bao gồm: Giờ vào/ra, số phút đi muộn, về sớm, OT, v.v.
    """
    reports = attendance_service.get_monthly_report(db, employee_id, month, year)
    return reports