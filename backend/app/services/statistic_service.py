from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, asc, not_
from datetime import datetime, timedelta
from app.models.employee import Employee
from app.models.daily_work_report import DailyWorkReport
from app.models.absence import Absence, AbsenceType

class StatisticService:
    def get_dashboard_stats(self, db: Session, months_back: int):
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=months_back * 30)

        excluded_types = [
            AbsenceType.MATERNITY, 
            AbsenceType.WEDDING, 
            AbsenceType.FUNERAL, 
            AbsenceType.PATERNITY
        ]

        # 1. Query Top Chăm Chỉ
        top_hard_working_raw = db.query(
            Employee.id.label("employee_id"),
            Employee.full_name,
            func.coalesce(func.sum(DailyWorkReport.late_arrive_minutes + DailyWorkReport.leave_early_minutes), 0).label("total_offence"),
            func.count(Absence.id).label("total_abs")
        ).outerjoin(DailyWorkReport, and_(
            Employee.id == DailyWorkReport.employee_id,
            DailyWorkReport.work_date.between(start_date, end_date)
        )).outerjoin(Absence, and_(
            Employee.id == Absence.employee_id,
            Absence.work_date.between(start_date, end_date),
            not_(Absence.absence_type.in_(excluded_types))
        )).group_by(Employee.id, Employee.full_name)\
        .order_by(asc("total_abs"), asc("total_offence"))\
        .limit(10).all()

        # 2. Query Top Về Muộn
        late_leavers_raw = db.query(
            Employee.id.label("employee_id"),
            Employee.full_name,
            DailyWorkReport.check_out,
            DailyWorkReport.work_date
        ).join(DailyWorkReport, Employee.id == DailyWorkReport.employee_id)\
        .filter(DailyWorkReport.work_date.between(start_date, end_date))\
        .order_by(desc(DailyWorkReport.check_out))\
        .limit(10).all()

        # 3. Tính toán Tỷ lệ (Ratios)
        total_days = db.query(func.count(DailyWorkReport.id))\
            .filter(DailyWorkReport.work_date.between(start_date, end_date)).scalar() or 0
        
        on_time_days = db.query(func.count(DailyWorkReport.id))\
            .filter(
                DailyWorkReport.work_date.between(start_date, end_date),
                DailyWorkReport.late_arrive_minutes == 0,
                DailyWorkReport.leave_early_minutes == 0
            ).scalar() or 0

        on_time_pct = round((on_time_days / total_days * 100), 2) if total_days > 0 else 0
        late_early_pct = 100 - on_time_pct if total_days > 0 else 0

        # --- MAPPING DATA ĐỂ FIX LỖI VALIDATION ---
        return {
            "top_hard_working": [
                {
                    "employee_id": r.employee_id,
                    "full_name": r.full_name,
                    "total_offence_minutes": int(r.total_offence),
                    "total_absences": int(r.total_abs)
                } for r in top_hard_working_raw
            ],
            "top_late_leavers": [
                {
                    "employee_id": l.employee_id,
                    "full_name": l.full_name,
                    "last_check_out": l.check_out,
                    "on_date": l.work_date
                } for l in late_leavers_raw
            ],
            "ratios": {
                "on_time_percentage": on_time_pct,
                "late_early_percentage": late_early_pct,
                "absent_percentage": 0.0
            }
        }

statistic_service = StatisticService()