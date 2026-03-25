from fastapi import FastAPI

from app.db.session import Base, engine
from app.models import absence_tracker, absence, attendance_correction, attendance_log, daily_work_report, employee_benefit_log, employee, notification, overtime_request, shift_change_request, shift, system_setting, timesheet_monthly_summary, timesheet_period_control, vacation
from app.api.v1.calendar import router as calendar_router

def init_db():
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="Timesheet API", version="1.0")
init_db()

app.include_router(calendar_router, prefix="/api/v1")
