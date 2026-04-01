from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import extract, func

from app.models.overtime_request import OvertimeRequest
from app.models.absence import ApprovalStatus
from app.schemas.overtime_request import OvertimeCreate, OvertimeApprove
from app.models.employee import Employee
from app.models.shift import Shift
from app.core.config import OVER_TIME_MONTHLY_LIMIT_MINS, OVER_TIME_YEARLY_LIMIT_MINS, OVERTIME_DAILY_LIMIT_MINS

class OvertimeService:
    def create_request(self, db: Session, obj_in: OvertimeCreate, emp_id: int):
        multiplier_value = obj_in.ot_type.multiplier
        
        employee = db.query(Employee).options(joinedload(Employee.shift)).filter(
            Employee.id == emp_id
        ).first()
        if not employee or not employee.shift:
            raise HTTPException(
                status_code=404, 
                detail="Không tìm thấy thông tin nhân viên hoặc ca làm việc của nhân viên này."
            )

        shift : Shift = employee.shift
        
        is_outside_shift = (obj_in.end_time <= shift.start_time) or (obj_in.start_time >= shift.end_time)

        if not is_outside_shift:
            raise HTTPException(
                status_code=400,
                detail=f"Thời gian OT không được trùng với ca làm việc {shift.name}."
            )

        current_month_total = db.query(func.sum(OvertimeRequest.actual_work_time)).filter(
            OvertimeRequest.employee_id == emp_id,
            OvertimeRequest.status != ApprovalStatus.REJECTED,
            extract('month', OvertimeRequest.work_date) == obj_in.work_date.month,
            extract('year', OvertimeRequest.work_date) == obj_in.work_date.year
        ).scalar() or 0

        calc_minutes = (obj_in.end_time.hour * 60 + obj_in.end_time.minute) - \
                (obj_in.start_time.hour * 60 + obj_in.start_time.minute)

        if calc_minutes > OVERTIME_DAILY_LIMIT_MINS:
            raise HTTPException(
                status_code=400,
                detail=f"Vi phạm định mức: Thời gian OT không được vượt quá {OVERTIME_DAILY_LIMIT_MINS/60} giờ một ngày"
            )

        if current_month_total + calc_minutes > OVER_TIME_MONTHLY_LIMIT_MINS:
            raise HTTPException(
                status_code=400,
                detail=f"Vi phạm định mức: Tổng giờ làm thêm trong tháng không được quá 40 giờ. "
                    f"Bạn đã làm {current_month_total/60:.1f}h, đơn này thêm {calc_minutes/60:.1f}h."
            )

        current_year_total = db.query(func.sum(OvertimeRequest.actual_work_time)).filter(
            OvertimeRequest.employee_id == emp_id,
            OvertimeRequest.status != ApprovalStatus.REJECTED,
            extract('year', OvertimeRequest.work_date) == obj_in.work_date.year
        ).scalar() or 0

        if current_year_total + calc_minutes > OVER_TIME_YEARLY_LIMIT_MINS:
            raise HTTPException(
                status_code=400,
                detail=f"Vi phạm định mức: Tổng giờ làm thêm trong năm không được quá 200 giờ. "
                    f"Hiện tại đã tích lũy {current_year_total/60:.1f}h."
            )

        db_obj = OvertimeRequest(
            **obj_in.model_dump(),
            employee_id=emp_id,
            multiplier=multiplier_value,
            status=ApprovalStatus.PENDING
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_pending_request(self, db: Session, ot_id: int, emp_id: int):
        db_obj = db.query(OvertimeRequest).filter(
            OvertimeRequest.id == ot_id,
            OvertimeRequest.employee_id == emp_id
        ).first()

        if not db_obj:
            raise HTTPException(404, "Không tìm thấy đơn OT")

        if db_obj.status != ApprovalStatus.PENDING:
            raise HTTPException(400, "Chỉ có thể xóa đơn đang chờ duyệt (PENDING)")

        db.delete(db_obj)
        db.commit()
        return True

    def approve_request(self, db: Session, ot_id: int, admin_id: int, obj_in: OvertimeApprove):
        db_obj = db.query(OvertimeRequest).filter(OvertimeRequest.id == ot_id).first()
        if not db_obj:
            raise HTTPException(404, "Không tìm thấy đơn OT")

        db_obj.status = obj_in.status
        db_obj.approved_by = admin_id
        db_obj.approved_at = datetime.now()
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

overtime_service = OvertimeService()