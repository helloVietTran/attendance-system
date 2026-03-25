from fastapi import FastAPI

from app.db.session import Base, engine
from app.models import absence_tracker, absence, attendance_correction, attendance_log, daily_work_report, employee_benefit_log, employee, notification, overtime_request, shift_change_request, shift, system_setting, timesheet_monthly_summary, timesheet_period_control, vacation

def init_db():
    # Lệnh này sẽ tạo toàn bộ bảng trong Database
    Base.metadata.create_all(bind=engine)

app = FastAPI()
init_db()
