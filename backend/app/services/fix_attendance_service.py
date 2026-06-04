from sqlalchemy.orm import Session
from sqlalchemy import extract, and_, desc
from fastapi import HTTPException
from datetime import datetime
import math

from app.models.employee import Employee
from app.models.attendance_correction import AttendanceCorrection
from app.models.daily_work_report import DailyWorkReport
from app.services.setting_service import setting_service
from app.schemas.attendance_correction import CorrectionCreate
from app.models.absence import ApprovalStatus
from app.models.timesheet_period_control import TimesheetPeriodControl
from app.schemas.base import PaginationMetadata

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

    def update_correction_status(self, db: Session, correction_id: int, admin_id: int, status: ApprovalStatus):
        """Admin/HR Phê duyệt hoặc Từ chối yêu cầu sửa công"""

        fix_req = db.query(AttendanceCorrection).filter(AttendanceCorrection.id == correction_id).first()
        if not fix_req or fix_req.status != ApprovalStatus.PENDING:
            raise HTTPException(status_code=400, detail="Yêu cầu không hợp lệ hoặc đã xử lý.")

        if status == ApprovalStatus.APPROVED:
            # Kiểm tra kỳ chốt công
            locked_period = db.query(TimesheetPeriodControl).filter(
                TimesheetPeriodControl.month == fix_req.work_date.month,
                TimesheetPeriodControl.year == fix_req.work_date.year,
                TimesheetPeriodControl.is_locked == True
            ).first()

            if locked_period and fix_req.work_date < locked_period.closing_date:
                raise HTTPException(
                    status_code=400,
                    detail=f"Không thể phê duyệt. Ngày {fix_req.work_date} đã chốt (trước {locked_period.closing_date})."
                )

        fix_req.status = status
        fix_req.approved_by = admin_id

        try:
            db.commit()
            db.refresh(fix_req)

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Lỗi hệ thống khi cập nhật trạng thái.")

        return fix_req
    
    def get_my_corrections(self, db: Session, employee_id: int, month: int = None, year: int = None):
        query = db.query(AttendanceCorrection).filter(AttendanceCorrection.employee_id == employee_id)
        
        if month:
            query = query.filter(extract('month', AttendanceCorrection.work_date) == month)
        if year:
            query = query.filter(extract('year', AttendanceCorrection.work_date) == year)
            
        return query.order_by(AttendanceCorrection.work_date.desc()).all()
    
    def get_all_corrections_admin(
        self, db: Session, month: int, year: int, 
        status: str = None, search: str = None, 
        page: int = 1, limit: int = 10
    ):
        query = db.query(AttendanceCorrection).join(
            Employee, AttendanceCorrection.employee_id == Employee.id
        )

        query = query.filter(
            and_(
                extract('month', AttendanceCorrection.work_date) == month,
                extract('year', AttendanceCorrection.work_date) == year
            )
        )
        
        if status:
            query = query.filter(AttendanceCorrection.status == status)

        if search:
            query = query.filter(Employee.full_name.ilike(f"%{search}%"))

        total_elements = query.count()
        total_pages = math.ceil(total_elements / limit) if total_elements > 0 else 0
        skip = (page - 1) * limit

        results = query.add_columns(Employee.full_name)\
            .order_by(desc(AttendanceCorrection.created_at))\
            .offset(skip).limit(limit).all()

        data = []
        for correction, full_name in results:
            
            correction.employee_name = full_name
            data.append(correction)

        metadata = PaginationMetadata(
            total_elements=total_elements,
            total_pages=total_pages,
            page=page,
            limit=limit
        )

        return data, metadata

fix_attendance_service = FixAttendanceService()