from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from datetime import date, datetime
from sqlalchemy import extract, func

from app.models.overtime_request import OvertimeRequest
from app.models.absence import ApprovalStatus
from app.schemas.overtime_request import OvertimeCreate, OvertimeApprove
from app.models.employee import Employee
from app.models.shift import Shift
from app.core.config import OVER_TIME_MONTHLY_LIMIT_MINS, OVER_TIME_YEARLY_LIMIT_MINS, OVERTIME_DAILY_LIMIT_MINS
from app.models.attendance_log import AttendanceLog
from app.services.calendar_service import calendar_service

class OvertimeService:
    def create_request(self, db: Session, obj_in: OvertimeCreate, emp_id: int):
        multiplier_value = obj_in.ot_type.multiplier
        
        employee = db.query(Employee).options(joinedload(Employee.shift)).filter(
            Employee.id == emp_id
        ).first()
        if not employee or not employee.shift:
            raise HTTPException(
                status_code=404, 
                detail="Không tìm thấy thông tin nhân viên hoặc ca làm việc của nhân viên này."
            )

        shift : Shift = employee.shift
        
        is_outside_shift = (obj_in.end_time <= shift.start_time) or (obj_in.start_time >= shift.end_time)

        if not is_outside_shift:
            raise HTTPException(
                status_code=400,
                detail=f"Thời gian OT không được trùng với ca làm việc {shift.name}."
            )

        current_month_total = db.query(func.sum(OvertimeRequest.actual_work_time)).filter(
            OvertimeRequest.employee_id == emp_id,
            OvertimeRequest.status != ApprovalStatus.REJECTED,
            extract('month', OvertimeRequest.work_date) == obj_in.work_date.month,
            extract('year', OvertimeRequest.work_date) == obj_in.work_date.year
        ).scalar() or 0

        calc_minutes = (obj_in.end_time.hour * 60 + obj_in.end_time.minute) - \
                (obj_in.start_time.hour * 60 + obj_in.start_time.minute)

        if calc_minutes > OVERTIME_DAILY_LIMIT_MINS:
            raise HTTPException(
                status_code=400,
                detail=f"Vi phạm định mức: Thời gian OT không được vượt quá {OVERTIME_DAILY_LIMIT_MINS/60} giờ một ngày"
            )

        if current_month_total + calc_minutes > OVER_TIME_MONTHLY_LIMIT_MINS:
            raise HTTPException(
                status_code=400,
                detail=f"Vi phạm định mức: Tổng giờ làm thêm trong tháng không được quá 40 giờ. "
                    f"Bạn đã làm {current_month_total/60:.1f}h, đơn này thêm {calc_minutes/60:.1f}h."
            )

        current_year_total = db.query(func.sum(OvertimeRequest.actual_work_time)).filter(
            OvertimeRequest.employee_id == emp_id,
            OvertimeRequest.status != ApprovalStatus.REJECTED,
            extract('year', OvertimeRequest.work_date) == obj_in.work_date.year
        ).scalar() or 0

        if current_year_total + calc_minutes > OVER_TIME_YEARLY_LIMIT_MINS:
            raise HTTPException(
                status_code=400,
                detail=f"Vi phạm định mức: Tổng giờ làm thêm trong năm không được quá 200 giờ. "
                    f"Hiện tại đã tích lũy {current_year_total/60:.1f}h."
            )

        db_obj = OvertimeRequest(
            **obj_in.model_dump(),
            employee_id=emp_id,
            multiplier=multiplier_value,
            status=ApprovalStatus.PENDING
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_pending_request(self, db: Session, ot_id: int, emp_id: int):
        db_obj = db.query(OvertimeRequest).filter(
            OvertimeRequest.id == ot_id,
            OvertimeRequest.employee_id == emp_id
        ).first()

        if not db_obj:
            raise HTTPException(404, "Không tìm thấy đơn OT")

        if db_obj.status != ApprovalStatus.PENDING:
            raise HTTPException(400, "Chỉ có thể xóa đơn đang chờ duyệt (PENDING)")

        db.delete(db_obj)
        db.commit()
        return True

    def approve_request(self, db: Session, ot_id: int, admin_id: int, obj_in: OvertimeApprove):
        db_obj = db.query(OvertimeRequest).filter(OvertimeRequest.id == ot_id).first()
        if not db_obj:
            raise HTTPException(404, "Không tìm thấy đơn OT")

        db_obj.status = obj_in.status
        db_obj.approved_by = admin_id
        db_obj.approved_at = datetime.now()
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def _time_to_minutes(self, t) -> int:
        if t is None: return 0
        return t.hour * 60 + t.minute

    def calculate_actual_ot_minutes(self, db: Session, ot_id: int):
        """
        Duyệt đơn OT và tính toán số phút thực tế dựa trên Attendance Log
        """
        ot_req = db.query(OvertimeRequest).filter(OvertimeRequest.id == ot_id).first()
        if not ot_req:
            return None

        # lấy log đầu và cuối của nhân viên trong ngày đó
        logs = db.query(AttendanceLog).filter(
            AttendanceLog.employee_id == ot_req.employee_id,
            AttendanceLog.log_date == ot_req.work_date
        ).order_by(AttendanceLog.checked_time.asc()).all()

        if not logs:
            ot_req.actual_work_time = 0
            db.commit()
            return 0

        first_log_min = self._time_to_minutes(logs[0].checked_time)
        last_log_min = self._time_to_minutes(logs[-1].checked_time)
        total_presence_min = last_log_min - first_log_min

        working_days = calendar_service.get_working_days_list(db, ot_req.work_date, ot_req.work_date)
        is_working_day = len(working_days) > 0

        actual_ot = 0
        lunch_break = 60
        if is_working_day:
            # Ngày đi làm: Lấy tổng thời gian - 480p hành chính - 60p nghỉ trưa
           
            standard_work = 480
            actual_ot = total_presence_min - standard_work - lunch_break
        else:
            actual_ot = total_presence_min - lunch_break

        registered_min = self._time_to_minutes(ot_req.end_time) - self._time_to_minutes(ot_req.start_time)
        
        final_ot_min = max(0, min(actual_ot, registered_min))
        
        ot_req.actual_work_time = final_ot_min
        db.commit()
        return final_ot_min

    def batch_process_actual_ot(self, db: Session, target_date: date):
        """
        Hàm chạy định kỳ để cập nhật giờ OT thực tế cho tất cả đơn trong 1 ngày
        """
        requests = db.query(OvertimeRequest).filter(
            OvertimeRequest.work_date == target_date,
            OvertimeRequest.status == ApprovalStatus.APPROVED
        ).all()
        
        for req in requests:
            self.calculate_actual_ot_minutes(db, req.id)
        
        return len(requests)

overtime_service = OvertimeService()