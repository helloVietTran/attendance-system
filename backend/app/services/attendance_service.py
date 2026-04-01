from sqlalchemy.orm import Session
from sqlalchemy import extract, and_
from datetime import date, time
from fastapi import HTTPException

from app.models.attendance_log import AttendanceLog
from app.models.daily_work_report import DailyWorkReport
from app.models.absence import Absence, ApprovalStatus
from app.models.overtime_request import OvertimeRequest

from app.schemas.attendance_log import AttendanceCreate

from app.services.setting_service import setting_service

class AttendanceService:
    def ingest_log(self, db: Session, obj_in: AttendanceCreate):
        """Ghi nhận một lượt chấm công mới"""
        db_obj = AttendanceLog(
            employee_id=obj_in.employee_id,
            log_date=obj_in.log_date,
            shift_start=obj_in.shift_start,
            shift_end=obj_in.shift_end,
            checked_time=obj_in.checked_time
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_attendance_logs_by_month(self, db: Session, employee_id: int, month: int, year: int):
        """Lấy danh sách chấm công của nhân viên trong một tháng cụ thể"""
        return db.query(AttendanceLog).filter(
            AttendanceLog.employee_id == employee_id,
            extract('month', AttendanceLog.log_date) == month,
            extract('year', AttendanceLog.log_date) == year
        ).order_by(AttendanceLog.log_date.asc(), AttendanceLog.checked_time.asc()).all()

    def process_daily_attendance(self, db: Session, employee_id: int, work_date: date):
        # lấy các setting cần thiết
        lunch_start_str = setting_service.get_setting_value(db, "lunch_break_start")
        lunch_end_str = setting_service.get_setting_value(db, "lunch_break_end")
        required_minutes = int(setting_service.get_setting_value(db, "required_work_minutes", 480))

        if not lunch_start_str or not lunch_end_str:
            raise HTTPException(status_code=400, detail="Hệ thống chưa cấu hình khung giờ làm việc chuẩn.")

        # lấy log đầu tiên và cuối cùng trong ngày
        logs = db.query(AttendanceLog).filter(
            AttendanceLog.employee_id == employee_id,
            AttendanceLog.log_date == work_date
        ).order_by(AttendanceLog.checked_time.asc()).all()

        has_absence = db.query(Absence).filter(
            Absence.employee_id == employee_id,
            Absence.status == ApprovalStatus.APPROVED,
            Absence.start_date <= work_date,
            Absence.end_date >= work_date
        ).first()

        if has_absence or not logs:
              raise HTTPException(status_code=400, detail="Không tìm thấy dữ liệu chấm công hoặc nhân viên xin nghỉ.")

        first_log = logs[0]
        last_log = logs[-1]

        # Convert sang minutes
        check_in_min = self._time_to_minutes(str(first_log.checked_time)[:5])
        check_out_min = self._time_to_minutes(str(last_log.checked_time)[:5])

        shift_start_min = self._time_to_minutes(str(first_log.shift_start)[:5])
        shift_end_min = self._time_to_minutes(str(first_log.shift_end)[:5])

        lunch_start_min = self._time_to_minutes(lunch_start_str)
        lunch_end_min = self._time_to_minutes(lunch_end_str)

        in_office = check_out_min - check_in_min

        # Trừ giờ nghỉ trưa (Overlap giữa giờ làm và giờ nghỉ)
        overlap_lunch = self._get_overlap_minutes(check_in_min, check_out_min, lunch_start_min, lunch_end_min)
        actual_work_time = in_office - overlap_lunch

        # Tính đi muộn về sớm
        late_minutes = max(0, check_in_min - shift_start_min)
        early_minutes = max(0, shift_end_min - check_out_min)

        # Tính thiếu giờ / thừa giờ (OT)
        lack_minutes = max(0, required_minutes - actual_work_time)
        overtime_minutes = max(0, actual_work_time - required_minutes)

        # Tính thời gian OT
        if overtime_minutes > 0:
            ot_request = db.query(OvertimeRequest).filter(
                OvertimeRequest.employee_id == employee_id,
                OvertimeRequest.work_date == work_date,
                OvertimeRequest.status == ApprovalStatus.APPROVED
            ).first()

            if ot_request:
                registered_duration = self._calculate_minutes(ot_request.start_time, ot_request.end_time)
                ot_request.actual_work_time = min(registered_duration, overtime_minutes)

        daily_report = db.query(DailyWorkReport).filter(
            DailyWorkReport.employee_id == employee_id, 
            DailyWorkReport.work_date == work_date
        ).first()

        if not daily_report:
            daily_report = DailyWorkReport(employee_id=employee_id, work_date=work_date)
            db.add(daily_report)

        daily_report.check_in = str(first_log.checked_time)[:5]
        daily_report.check_out = str(last_log.checked_time)[:5]
        daily_report.in_office_minutes = in_office
        daily_report.work_time_minutes = actual_work_time
        daily_report.late_arrive_minutes = late_minutes
        daily_report.leave_early_minutes = early_minutes
        daily_report.lack_minutes = lack_minutes
        daily_report.overtime_minutes = overtime_minutes

        db.commit()
        db.refresh(daily_report)
        return daily_report

    def get_daily_work_reports_by_month(self, db: Session, employee_id: int, month: int, year: int):
        return db.query(DailyWorkReport).filter(
            and_(
                DailyWorkReport.employee_id == employee_id,
                extract('month', DailyWorkReport.work_date) == month,
                extract('year', DailyWorkReport.work_date) == year
            )
        ).order_by(DailyWorkReport.work_date.asc()).all()

    def _time_to_minutes(self, time_str: str) -> int:
        if not time_str: return 0
        h, m = map(int, time_str.split(':'))
        return h * 60 + m

    def _get_overlap_minutes(self, start1, end1, start2, end2) -> int:
        """Tính số phút trùng nhau giữa 2 khoảng thời gian"""
        start = max(start1, start2)
        end = min(end1, end2)
        return max(0, end - start)

    def _calculate_minutes(self, start: time, end: time) -> int:
        """
        Tính toán số phút giữa hai mốc thời gian trong cùng một ngày.
        Ví dụ: 18:00 đến 20:30 -> 150 phút.
        """
        start_total_minutes = start.hour * 60 + start.minute

        end_total_minutes = end.hour * 60 + end.minute

        duration = end_total_minutes - start_total_minutes

        return max(0, duration)

attendance_service = AttendanceService()