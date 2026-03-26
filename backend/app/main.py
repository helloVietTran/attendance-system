from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.session import init_db, SessionLocal
from app.api.v1.calendar import router as calendar_router
from app.api.v1.settings import router as setting_router
from app.api.v1.attendance import router as attendance_router
from app.api.v1.shift import router as shift_router
from app.api.v1.employee import router as employee_router
from app.api.v1.notification import router as notification_router
from app.api.v1.fix_attendance import router as fix_attendance_router
from app.api.v1.absences import router as absence_router
from app.api.v1.payroll import router as payroll_router

from app.services.setting_service import setting_service
from app.models import (
    absence_tracker, absence, attendance_correction, attendance_log, 
    daily_work_report, employee_benefit_log, employee, notification, 
    overtime_request, shift_change_request, shift, system_setting, 
    timesheet_monthly_summary, timesheet_period_control, vacation
)
from app.core.scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    db = SessionLocal()
    try:
        setting_service.preload_all_settings(db)
        start_scheduler()

    except Exception as e:
        print(f"Lỗi khi nạp settings: {e}")
    finally:
        db.close()
    yield

    setting_service._cache.clear()

app = FastAPI(
    title="Timesheet API", 
    version="1.0",
    lifespan=lifespan
)

# Đăng ký Router
app.include_router(calendar_router, prefix="/api/v1")
app.include_router(setting_router, prefix="/api/v1")
app.include_router(attendance_router, prefix="/api/v1")
app.include_router(shift_router, prefix="/api/v1")
app.include_router(employee_router, prefix="/api/v1")
app.include_router(notification_router, prefix="/api/v1")
app.include_router(fix_attendance_router, prefix="/api/v1")
app.include_router(absence_router, prefix="/api/v1")
app.include_router(payroll_router, prefix="/api/v1")