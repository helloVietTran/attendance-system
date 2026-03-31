from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware

from app.db.session import init_db, SessionLocal
from app.api.v1.calendar import router as calendar_router
from app.api.v1.setting import router as setting_router
from app.api.v1.attendance import router as attendance_router
from app.api.v1.shift import router as shift_router
from app.api.v1.employee import router as employee_router
from app.api.v1.notification import router as notification_router
from app.api.v1.fix_attendance import router as fix_attendance_router
from app.api.v1.absence import router as absence_router
from app.api.v1.payroll import router as payroll_router
from app.api.v1.auth import router as auth_router
from app.api.v1.admin import router as admin_router
from app.api.v1.overtime import router as overtime_router
from app.api.v1.face_auth import router as face_auth_router

from fastapi.exceptions import HTTPException, RequestValidationError
from app.core.exception import http_exception_handler, validation_exception_handler

from app.services.setting_service import setting_service
from app.models import (
    absence_tracker, absence, attendance_correction, attendance_log, 
    daily_work_report, employee_benefit_log, employee, notification, 
    overtime_request, shift_change_request, shift, system_setting, 
    timesheet_period_control, vacation
)
from app.core.scheduler import start_scheduler
from app.core.config import SECRET_KEY

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

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY, 
    session_cookie="ATS_SESSION_ID" 
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

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
app.include_router(auth_router, prefix="/api/v1" )
app.include_router(admin_router, prefix="/api/v1")
app.include_router(overtime_router, prefix="/api/v1")
app.include_router(face_auth_router, prefix="/api/v1")