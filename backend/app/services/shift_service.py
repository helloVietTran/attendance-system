from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, date
from fastapi import HTTPException
from app.models.shift_change_request import ShiftChangeRequest, RequestStatus
from app.models.employee import Employee
from app.schemas.shift_change_request import ShiftChangeCreate

class ShiftService:
    def create_request(self, db: Session, employee_id: int, obj_in: ShiftChangeCreate):
        # Xác định tháng sau
        today = date.today()
        target_month = today.month + 1
        target_year = today.year
        
        if target_month > 12:
            target_month = 1
            target_year += 1

        # check nhân viên
        emp = db.query(Employee).filter(Employee.id == employee_id).first()
        if not emp:
            raise HTTPException(status_code=404, detail="Nhân viên không tồn tại")
        
        # kiểm tra xem đã có yêu cầu PENDING nào cho tháng đó chưa
        existing = db.query(ShiftChangeRequest).filter(
            and_(
                ShiftChangeRequest.employee_id == employee_id,
                ShiftChangeRequest.target_month == target_month,
                ShiftChangeRequest.target_year == target_year,
                ShiftChangeRequest.status == RequestStatus.PENDING
            )
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Bạn đã có một yêu cầu đang chờ duyệt cho tháng sau")

        db_obj = ShiftChangeRequest(
            employee_id=employee_id,
            target_month=target_month,
            target_year=target_year,
            old_shift_id=obj_in.current_shift_id,
            new_shift_id=obj_in.new_shift_id,
            reason=obj_in.reason,
            status=RequestStatus.PENDING
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def approve_request(self, db: Session, request_id: int, admin_id: int):
        """HR phê duyệt yêu cầu đổi ca"""
        req = db.query(ShiftChangeRequest).filter(ShiftChangeRequest.id == request_id).first()
        
        if not req:
            raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu")
        if req.status != RequestStatus.PENDING:
            raise HTTPException(status_code=400, detail="Yêu cầu này đã được xử lý trước đó")

        # cập nhật trạng thái yêu cầu
        req.status = RequestStatus.APPROVED
        req.processed_by = admin_id
        req.processed_at = datetime.now()

        # sau đó cho một cron job chạy vào 1h sáng đầu tháng để cập nhật ca làm việc của nhân viên

        db.commit()
        db.refresh(req)
        return req

shift_service = ShiftService()