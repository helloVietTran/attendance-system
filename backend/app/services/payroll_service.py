import calendar
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from datetime import datetime
from typing import List, Dict

from app.models.employee import Employee
from app.models.daily_work_report import DailyWorkReport
from app.models.monthly_report import MonthlyWorkReport
from app.models.absence import Absence, ApprovalStatus
from app.models.attendance_correction import AttendanceCorrection
from app.models.timesheet_period_control import TimesheetPeriodControl

class PayrollService:
    def _get_debt_adjustment(self, db: Session, employee_id: int, first_day_current_month: date):
        """
        Tính nợ công tháng trước: thực tế - tạm tính. Trả về một số âm
        """
        last_month_end_date = first_day_current_month - timedelta(days=1)
        first_day_last_month = last_month_end_date.replace(day=1)

        # lấy ngày chốt công kỳ chốt công trước để truy vấn
        last_period_control = db.query(TimesheetPeriodControl).filter(
            TimesheetPeriodControl.month == first_day_last_month.month,
            TimesheetPeriodControl.year == first_day_last_month.year
        ).first()

        if not last_period_control:
            return 0 # Không có dữ liệu kỳ trước thì nợ = 0

        # lấy tổng hợp tháng trước
        last_month_report = db.query(MonthlyWorkReport).filter(
            MonthlyWorkReport.employee_id == employee_id,
            MonthlyWorkReport.period_start == first_day_last_month
        ).first()

        if not last_month_report or last_month_report.estimated_minutes == 0:
            return 0

        # tính thực tế tính từ ngày chốt công tháng trước đến cuối tháng trước
        actual_end_of_last_month = db.query(func.sum(DailyWorkReport.work_time_minutes)).filter(
            DailyWorkReport.employee_id == employee_id,
            DailyWorkReport.work_date >= last_period_control.closing_date,
            DailyWorkReport.work_date <= last_month_end_date
        ).scalar() or 0
        
        debt = actual_end_of_last_month - last_month_report.estimated_minutes
        return debt
    
    def _calculate_estimated_minutes(self, start_date: date, end_date: date):
        """Tính phút tạm tính cho các ngày tương lai (trừ T7, CN)"""

        estimated = 0
        curr = start_date
        while curr <= end_date:
            if curr.weekday() < 5: # T2 -> T6
                estimated += 480
            curr += timedelta(days=1)
        return estimated
    
    def _calculate_actual_metrics(self, db: Session, employee_id: int, actual_reports: List[DailyWorkReport]) -> Dict[str, int]:
        totals = {
            "work": 0,
            "lack": 0
        }

        for report in actual_reports:
            # Rule 1: Yêu cầu fix công được duyệt -> Tính đủ 480p, bỏ qua bù trừ
            has_correction = db.query(AttendanceCorrection).filter(
                AttendanceCorrection.employee_id == employee_id,
                AttendanceCorrection.work_date == report.work_date,
                AttendanceCorrection.status == ApprovalStatus.APPROVED
            ).first()

            if has_correction:
                totals["work"] += 480
                continue

            totals["work"] += report.work_time_minutes or 0
            totals["lack"] += report.lack_minutes or 0
            totals["ot"] += report.overtime_minutes or 0

        return totals
    
    def close_monthly_payroll(self, db: Session, employee_id: int, closing_day: int = 20):
        today = date.today()

        first_day = today.replace(day=1)  
        last_day_of_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        
        # Thai sản, nghỉ ốm 1 tháng sẽ xử lý riêng
        is_special_leave = db.query(Absence).filter(
            Absence.employee_id == employee_id,
            Absence.status == ApprovalStatus.APPROVED,
            Absence.start_date <= last_day_of_month,
            Absence.end_date >= first_day,
            Absence.absence_type_id.in_([3, 4]) # 3: Thai sản, 4: Nghỉ ốm dài ngày
        ).first()

        if is_special_leave:
            print(f"Bỏ qua NV {employee_id} do đang nghỉ chế độ.")
            return None

        # duyệt bảng daily report (từ ngày 1 đến ngày chốt công - 1) VD: chốt công 20 -> tính từ 1 - 19
        actual_reports = db.query(DailyWorkReport).filter(
            DailyWorkReport.employee_id == employee_id,
            DailyWorkReport.work_date >= first_day,
            DailyWorkReport.work_date < today.replace(day=closing_day)
        ).all()

        actual_totals = self._calculate_actual_metrics(db, employee_id, actual_reports)

        # tính nợ công tháng trước và trừ đi nợ ở tháng hiện tại
        debt_adjustment = self._get_debt_adjustment(db, employee_id, first_day)
        total_work += actual_totals["work"] + debt_adjustment

        # tạm tính những ngày còn lại
        estimated_minutes = self._calculate_estimated_minutes(today.replace(day=closing_day), last_day_of_month)

        monthly_log = MonthlyWorkReport(
            employee_id=employee_id,
            period_start=first_day,
            period_end=last_day_of_month,
            work_minutes=total_work,
            lack_minutes=actual_totals["lack"],
            estimated_minutes=estimated_minutes
        )

        db.add(monthly_log)
        return monthly_log

    def calculate_all_employees_payroll(self, db: Session, closing_day: int = 20):
        """
        Hàm xử lý tập trung: Quản lý Transaction (Commit/Rollback)
        """
        employees: List[Employee] = db.query(Employee).all()
        processed_count = 0
        skipped_count = 0

        try:
            for emp in employees:
                result = self.close_monthly_payroll(db, emp.id, closing_day)
                if result:
                    processed_count += 1
                else:
                    skipped_count += 1
            
            db.commit()
            
            return {
                "status": "success",
                "total_employees": len(employees),
                "processed": processed_count,
                "skipped_special_leave": skipped_count
            }

        except Exception as e:
            db.rollback()
            print(f"Transaction failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Quá trình tính toán thất bại: {str(e)}")

    def lock_timesheet_period(self, db: Session, admin_id: int, month: int, year: int, closing_day: int = 20):
        """
        Sau khi thực hiện chốt công cho toàn bộ nhân viên và khóa kỳ công lại, sau khi khóa không cho fix request nữa
        """
        existing_period = db.query(TimesheetPeriodControl).filter(
            TimesheetPeriodControl.month == month,
            TimesheetPeriodControl.year == year
        ).first()

        if existing_period and existing_period.is_locked:
            raise HTTPException(status_code=400, detail=f"Kỳ công tháng {month}/{year} đã được khóa trước đó.")

        today = date.today()
        if not existing_period:
            new_control = TimesheetPeriodControl(
                month=month,
                year=year,
                closing_date=today,
                is_locked=True,
                locked_by=admin_id,
                locked_at=datetime.now(),
                note=f"Chốt công tháng {month} năm {year} vào ngày {closing_day}"
            )
            db.add(new_control)
        else:
            existing_period.is_locked = True
            existing_period.locked_by = admin_id
            existing_period.locked_at = datetime.now()
            existing_period.closing_date = today

        db.commit()
        return existing_period or new_control

payroll_service = PayrollService()