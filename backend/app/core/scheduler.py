from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.attendance_service import attendance_service
from app.models.employee import Employee
from datetime import date

def calculate_all_employees_attendance():
    """Hàm quét toàn bộ nhân viên và tính công ngày hôm nay"""
    db = SessionLocal()
    today = date.today()
    print(f"--- [CRON] Bắt đầu tổng hợp công ngày {today} lúc 18:00 ---")
    
    try:
        # 1. Lấy danh sách tất cả nhân viên đang hoạt động
        employees = db.query(Employee).all() 
        
        for emp in employees:
            try:
                # Hàm này sẽ lấy log đầu/cuối và save vào DailyWorkReport
                result = attendance_service.process_daily_attendance(db, emp.id, today)
                if result:
                    print(f"Successfully processed for Emp ID: {emp.id}")
            except Exception as e:
                print(f"Error processing Emp ID {emp.id}: {e}")
                
        db.commit()
    finally:
        db.close()
    print("--- [CRON] Kết thúc tổng hợp công ---")

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Chạy mỗi ngày vào lúc 18:00 (18 giờ 0 phút 0 giây)
    scheduler.add_job(
        calculate_all_employees_attendance, 
        'cron', 
        hour=18, 
        minute=0
    )
    scheduler.start()