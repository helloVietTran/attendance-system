from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date

from app.db.session import SessionLocal
from app.models.employee import Employee
from app.services.attendance_service import attendance_service
from app.services.benefit_service import benefit_service
from app.services.shift_service import shift_service

def calculate_all_employees_attendance():
    """Hàm quét toàn bộ nhân viên và tính công ngày hôm nay"""
    db = SessionLocal()
    today = date.today()
    try:
        employees = db.query(Employee).all() 
        
        for emp in employees:
            try:
                result = attendance_service.process_daily_attendance(db, emp.id, today)
                if result:
                    print(f"Successfully processed for Emp ID: {emp.id}")
            except Exception as e:
                print(f"Error processing Emp ID {emp.id}: {e}")
        db.commit()
    finally:
        db.close()


def monthly_shift_update_job():
    db = SessionLocal()
    try:
        count = shift_service.apply_monthly_shift_changes(db)
    except Exception as e:
        db.rollback()
    finally:
        db.close()

def check_birthdays_job():
    db = SessionLocal()
    try:
        benefit_service.process_daily_birthday_benefits(db)
    finally:
        db.close()

# TODO: retry
def start_scheduler():
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        calculate_all_employees_attendance, 
        'cron', 
        hour=23, 
        minute=0
    )

    scheduler.add_job(
        monthly_shift_update_job,
        'cron',
        day=1,
        hour=1,
        minute=0
    )

    scheduler.add_job(
        check_birthdays_job,
        'cron',
        hour=3,
        minute=0
    )

    scheduler.start()