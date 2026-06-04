from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date
from fastapi import HTTPException

from app.models.shift import Shift
from app.models.shift_change_request import ShiftChangeRequest, RequestStatus
from app.models.employee import Employee
from app.schemas.shift_change_request import ShiftChangeCreate
    
class ShiftService:
    def create_request(self, db: Session, employee_id: int, obj_in: ShiftChangeCreate):
        today = date.today()
        target_month = today.month + 1
        target_year = today.year
        
        if target_month > 12:
            target_month = 1
            target_year += 1

        emp = db.query(Employee).filter(Employee.id == employee_id).first()
        if not emp:
            raise HTTPException(status_code=404, detail="Nhân viên không tồn tại")

        db_obj = db.query(ShiftChangeRequest).filter(
            and_(
                ShiftChangeRequest.employee_id == employee_id,
                ShiftChangeRequest.target_month == target_month,
                ShiftChangeRequest.target_year == target_year
            )
        ).first()

        if db_obj:
            # CẬP NHẬT (Update)
            db_obj.old_shift_id = obj_in.current_shift_id
            db_obj.new_shift_id = obj_in.new_shift_id
            db_obj.reason = obj_in.reason
            db_obj.status = RequestStatus.APPROVED
        else:
            # TẠO MỚI (Create)
            db_obj = ShiftChangeRequest(
                employee_id=employee_id,
                target_month=target_month,
                target_year=target_year,
                old_shift_id=obj_in.current_shift_id,
                new_shift_id=obj_in.new_shift_id,
                reason=obj_in.reason,
                status=RequestStatus.APPROVED
            )
            db.add(db_obj)

        try:
            db.commit()
            db.refresh(db_obj)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Lỗi khi lưu yêu cầu đổi ca")
            
        return db_obj

    def get_all_shifts(self, db: Session):
        """Lấy toàn bộ danh sách ca làm việc đang hoạt động"""
        return db.query(Shift).filter(Shift.is_active == True).all()

shift_service = ShiftService()