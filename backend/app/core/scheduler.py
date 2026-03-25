from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date

from app.db.session import SessionLocal
from app.models.employee import Employee
from app.models.shift_change_request import ShiftChangeRequest, RequestStatus
from app.services.attendance_service import attendance_service

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

def apply_monthly_shift_changes():
    """
    Tự động cập nhật shift_id cho nhân viên dựa trên các yêu cầu đã duyệt
    Chạy vào 01:00 AM ngày 1 hàng tháng
    """
    db = SessionLocal()
    today = date.today()
    current_month = today.month
    current_year = today.year


    try:
        requests = db.query(ShiftChangeRequest).filter(
            ShiftChangeRequest.status == RequestStatus.APPROVED,
            ShiftChangeRequest.target_month == current_month,
            ShiftChangeRequest.target_year == current_year
        ).all()

        if not requests:
            print("Không có yêu cầu đổi ca nào cần áp dụng.")
            return

        for req in requests:
            # update shift id
            employee = db.query(Employee).filter(Employee.id == req.employee_id).first()
            if employee:
                old_id = employee.shift_id
                employee.shift_id = req.new_shift_id
            # logging here
        
        db.commit()
    except Exception as e:
        db.rollback()
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
        apply_monthly_shift_changes,
        'cron',
        day=1,
        hour=1,
        minute=0
    )

    scheduler.start()