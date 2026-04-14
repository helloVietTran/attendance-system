from sqlalchemy.orm import Session
from sqlalchemy import extract, and_
from datetime import date
from app.models.employee import Employee
from app.models.employee_benefit_log import EmployeeBenefitLog, BenefitType
from app.models.notification import Notification

class BenefitService:
    def process_daily_birthday_benefits(self, db: Session):
        """Quét toàn bộ nhân viên có sinh nhật hôm nay và tặng công"""
        today = date.today()
        
        # phát hiện ngày sinh nhật
        birthday_employees = db.query(Employee).filter(
            and_(
                extract('month', Employee.dob) == today.month,
                extract('day', Employee.dob) == today.day
            )
        ).all()

        if not birthday_employees:
            print(f"--- [BIRTHDAY] Ngày {today}: Không có ai sinh nhật hôm nay. ---")
            return

        for emp in birthday_employees:
            # kiểm tra xem hôm nay đã tặng chưa
            exists = db.query(EmployeeBenefitLog).filter(
                EmployeeBenefitLog.employee_id == emp.id,
                EmployeeBenefitLog.apply_date == today,
                EmployeeBenefitLog.benefit_type == BenefitType.BIRTHDAY
            ).first()

            if not exists:
                # (480 phút = 1 ngày công)
                benefit_log = EmployeeBenefitLog(
                    employee_id=emp.id,
                    benefit_type=BenefitType.BIRTHDAY,
                    work_value=480,
                    apply_date=today,
                    description=f"Quà tặng sinh nhật cho {emp.full_name}"
                )
                db.add(benefit_log)

                # gửi thông báo cho nhân viên
                notif = Notification(
                    employee_id=emp.id,
                    title="Chúc mừng sinh nhật!",
                    content=f"Chúc mừng sinh nhật {emp.full_name}! Bạn vừa được tặng 1 ngày công vào hệ thống.",
                    notification_type="BIRTHDAY"
                )
                db.add(notif)
            

        db.commit()

benefit_service = BenefitService()