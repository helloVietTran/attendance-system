from sqlalchemy.orm import Session
from sqlalchemy import extract, and_
from fastapi import HTTPException
from datetime import datetime
from app.models.attendance_correction import AttendanceCorrection
from app.models.daily_work_report import DailyWorkReport
from app.services.setting_service import setting_service
from app.schemas.attendance_correction import CorrectionCreate
from app.models.absence import ApprovalStatus
from app.models.timesheet_period_control import TimesheetPeriodControl

class FixAttendanceService:
    def create_correction_request(self, db: Session, employee_id: int, obj_in: CorrectionCreate):
        max_allowed = int(setting_service._cache.get("max_attendance_correction_per_month", 3))

        # đếm số yêu cầu đã tạo trong tháng hiện tại
        today = datetime.now()
        count = db.query(AttendanceCorrection).filter(
            AttendanceCorrection.employee_id == employee_id,
            extract('month', AttendanceCorrection.work_date) == today.month,
            extract('year', AttendanceCorrection.work_date) == today.year,
            AttendanceCorrection.status != ApprovalStatus.REJECTED
        ).count()

        if count >= max_allowed:
            raise HTTPException(
                status_code=400, 
                detail=f"Bạn đã hết lượt gửi yêu cầu chỉnh sửa công trong tháng này (Tối đa {max_allowed} lần)."
            )
        
        work_report = db.query(DailyWorkReport).filter(
            DailyWorkReport.employee_id == employee_id,
            DailyWorkReport.work_date == obj_in.work_date
        ).first()

        if not work_report or work_report.lack_minutes <= 0:
            raise HTTPException(
                status_code=400, 
                detail="Ngày này bạn đã đủ công hoặc không có dữ liệu thiếu hụt để sửa."
            )

        # tạo request mới
        db_obj = AttendanceCorrection(
            employee_id=employee_id,
            work_date=obj_in.work_date,
            requested_check_in=obj_in.requested_check_in,
            requested_check_out=obj_in.requested_check_out,
            reason=obj_in.reason,
            status=ApprovalStatus.PENDING
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def approve_fix_request(self, db: Session, correction_id: int, admin_id: int):
        """HR Phê duyệt và cập nhật lại bảng DailyWorkReport"""
        fix_req = db.query(AttendanceCorrection).filter(AttendanceCorrection.id == correction_id).first()
        if not fix_req or fix_req.status != ApprovalStatus.PENDING:
            raise HTTPException(status_code=400, detail="Yêu cầu không hợp lệ hoặc đã xử lý.")
        
        locked_period = db.query(TimesheetPeriodControl).filter(
            TimesheetPeriodControl.month == fix_req.work_date.month,
            TimesheetPeriodControl.year == fix_req.work_date.year,
            TimesheetPeriodControl.is_locked == True
        ).first()

        # không cho phê duyệt nếu ngày công lỗi nằm trong kỳ đã CHỐT
        if locked_period:
            if fix_req.work_date < locked_period.closing_date:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Không thể phê duyệt. Ngày {fix_req.work_date} nằm trong khoảng "
                        f"đã chốt thực tế (trước ngày {locked_period.closing_date})."
                    )
                )

        fix_req.status = ApprovalStatus.APPROVED
        fix_req.approved_by = admin_id

        db.commit()
        db.refresh(fix_req)

        return fix_req
    
    def get_my_corrections(self, db: Session, employee_id: int, month: int = None, year: int = None):
        query = db.query(AttendanceCorrection).filter(AttendanceCorrection.employee_id == employee_id)
        
        if month:
            query = query.filter(extract('month', AttendanceCorrection.work_date) == month)
        if year:
            query = query.filter(extract('year', AttendanceCorrection.work_date) == year)
            
        return query.order_by(AttendanceCorrection.work_date.desc()).all()

fix_attendance_service = FixAttendanceService()