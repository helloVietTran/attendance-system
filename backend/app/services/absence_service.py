from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from fastapi import HTTPException
from datetime import datetime

from app.models.absence import Absence, AbsenceType, ApprovalStatus
from app.models.notification import Notification
from app.schemas.absence import AbsencePlanApprove, AbsencePlanCreate

from app.models.vacation import Vacation
from app.models.absence_tracker import AbsenceTracker
from app.models.absence_plan import AbsencePlan
from app.services.calendar_service import calendar_service
from app.models.employee import Employee

class AbsenceService:
    def get_my_plans(self, db: Session, emp_id: int, skip: int = 0, limit: int = 100):
        """Lấy danh sách kế hoạch nghỉ của cá nhân"""
        return db.query(AbsencePlan)\
            .filter(AbsencePlan.employee_id == emp_id)\
            .order_by(desc(AbsencePlan.start_date))\
            .offset(skip).limit(limit).all()

    def get_all_plans_admin(self, db: Session, status: str = None, search: str = None, skip: int = 0, limit: int = 100):
        query = db.query(AbsencePlan).join(Employee, AbsencePlan.employee_id == Employee.id)
        
        if status:
            query = query.filter(AbsencePlan.status == status)
        if search:
            query = query.filter(Employee.full_name.ilike(f"%{search}%"))
    
        total_elements = query.count()

        results = query.add_columns(Employee.full_name)\
                    .order_by(desc(AbsencePlan.created_at))\
                    .offset(skip)\
                    .limit(limit)\
                    .all()
        
        plans = []
        for plan_obj, full_name in results:
            plan_obj.employee_name = full_name 
            plans.append(plan_obj)
            
        return plans, total_elements
    
    def create_absence_plan(self, db: Session, obj_in: AbsencePlanCreate, emp_id: int):
        # Kiểm tra trùng lặp với các kế hoạch đã có (tránh gửi đơn đè nhau)
        overlap = db.query(AbsencePlan).filter(
            AbsencePlan.employee_id == emp_id,
            AbsencePlan.status != ApprovalStatus.REJECTED,
            and_(
                AbsencePlan.start_date <= obj_in.end_date,
                AbsencePlan.end_date >= obj_in.start_date
            )
        ).first()
        
        if overlap:
            raise HTTPException(status_code=400, detail="Bạn đã có một kế hoạch nghỉ trùng với thời gian này")

        # Tạo đơn Plan ở trạng thái PENDING
        db_plan = AbsencePlan(
            **obj_in.model_dump(),
            employee_id=emp_id,
            status=ApprovalStatus.PENDING
        )
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        return db_plan
    
    def approve_absence_plan(self, db: Session, plan_id: int, admin_id: int, obj_in: AbsencePlanApprove):
        plan = db.query(AbsencePlan).filter(AbsencePlan.id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Không tìm thấy kế hoạch nghỉ phép")

        if plan.status != ApprovalStatus.PENDING:
            raise HTTPException(
                status_code=400, 
                detail=f"Kế hoạch này đã được xử lý (Trạng thái: {plan.status.value})"
            )

        notif_title = ""
        notif_content = ""
        notif_type = ""

        if obj_in.status == ApprovalStatus.APPROVED:
            # --- LOGIC PHÊ DUYỆT ---
            tracker = db.query(AbsenceTracker).filter(AbsenceTracker.employee_id == plan.employee_id).first()
            if not tracker:
                raise HTTPException(status_code=404, detail="Không tìm thấy quỹ phép của nhân viên")

            # Lấy danh sách ngày làm việc (trừ lễ/cuối tuần) từ calendar_service
            working_days = calendar_service.get_working_days_list(db, plan.start_date, plan.end_date)
            
            abs_type = plan.absence_type
            special_paid_limit = abs_type.max_days
            days_processed = 0

            for current_date in working_days:
                is_paid = False
                days_processed += 1

                if abs_type == AbsenceType.ANNUAL:
                    # Nghỉ phép năm: Trừ thẳng vào quỹ
                    if tracker.total_remaining_leave > 0:
                        is_paid = True
                        tracker.deduct_leave(1)
                else:
                    # Nghỉ chế độ (Thai sản, cưới hỏi...)
                    if days_processed <= special_paid_limit:
                        is_paid = True
                    else:
                        # Vượt quá ngày chế độ -> Thử trừ vào quỹ phép năm
                        if tracker.total_remaining_leave > 0:
                            is_paid = True
                            tracker.deduct_leave(1)
                        else:
                            is_paid = False

                # Tạo bản ghi Absence chi tiết cho từng ngày
                daily_absence = Absence(
                    employee_id=plan.employee_id,
                    work_date=current_date,
                    is_paid=is_paid
                )
                db.add(daily_absence)

            notif_title = "Kế hoạch nghỉ phép đã được duyệt!"
            notif_content = f"Kế hoạch nghỉ từ {plan.start_date} đến {plan.end_date} của bạn đã được chấp thuận."
            notif_type = "ABSENCE_PLAN_APPROVED"

        elif obj_in.status == ApprovalStatus.REJECTED:
            notif_title = "Kế hoạch nghỉ phép bị từ chối"
            notif_content = f"Kế hoạch nghỉ của bạn không được duyệt. Lý do: {obj_in.note or 'Không có lý do cụ thể'}"
            notif_type = "ABSENCE_PLAN_REJECTED"

        plan.status = obj_in.status
        plan.approved_by = admin_id
        plan.approved_at = datetime.now()

        # Tạo thông báo
        if notif_title:
            new_notification = Notification(
                employee_id=plan.employee_id,
                title=notif_title,
                content=notif_content,
                notification_type=notif_type
            )
            db.add(new_notification)

        try:
            db.commit()
            db.refresh(plan)
            return plan
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

    def get_absences_by_employee(self, db: Session, employee_id: int):
        """Lấy danh sách đơn nghỉ của một nhân viên"""
        return db.query(Absence).filter(Absence.employee_id == employee_id).all()
    
    def delete_absence_plan(self, db: Session, plan_id: int, emp_id: int):
        plan = db.query(AbsencePlan).filter(
            AbsencePlan.id == plan_id,
            AbsencePlan.employee_id == emp_id
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=404, 
                detail="Không tìm thấy kế hoạch nghỉ phép này."
            )

        if plan.status != ApprovalStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Không thể xóa đơn ở trạng thái {plan.status.value}. "
                       f"Chỉ có đơn 'Chờ duyệt' mới được phép xóa."
            )

        try:
            db.delete(plan)
            db.commit()
            return {"message": "Đã xóa kế hoạch nghỉ phép thành công."}
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Có lỗi xảy ra khi xóa dữ liệu."
            )
            
    def get_leave_balance(self, db: Session, emp_id: int):
        tracker = db.query(AbsenceTracker).filter(AbsenceTracker.employee_id == emp_id).first()
        
        if not tracker:
            try:
                tracker = AbsenceTracker(
                    employee_id=emp_id,
                    current_year_total=14,
                    current_year_used=0,
                    carried_over_from_last_year=0,
                    carried_over_used=0
                )
                db.add(tracker)
                db.commit()
                db.refresh(tracker)
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=400, detail="Không thể khởi tạo quỹ phép cho nhân viên này")

        tracker.total_remaining = tracker.total_remaining_leave
        
        return tracker

absence_service = AbsenceService()