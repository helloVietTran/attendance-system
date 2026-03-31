
from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException
from app.models.absence import Absence, ApprovalStatus
from app.models.employee import Employee
from app.models.notification import Notification
from app.schemas.absence import AbsenceCreate, AbsenceApprove, LongTermAbsenceCreate

class AbsenceService:
    def create_absence(self, db: Session, obj_in: AbsenceCreate, empId):
        """Tạo đơn xin nghỉ phép với kiểm tra trùng lặp thời gian"""
        emp = db.query(Employee).filter(Employee.id == empId).first()
        if not emp:
            raise HTTPException(status_code=404, detail="Nhân viên không tồn tại")

        # kiểm tra trùng lặp (Overlap) với các đơn chưa bị từ chối
        overlap_check = db.query(Absence).filter(
            Absence.employee_id == empId,
            Absence.status != ApprovalStatus.REJECTED, 
            and_(
                Absence.start_date <= obj_in.end_date,
                Absence.end_date >= obj_in.start_date
            )
        ).first()

        if overlap_check:
            raise HTTPException(
                status_code=400, 
                detail=f"Nhân viên đã có đơn nghỉ phép từ {overlap_check.start_date} đến {overlap_check.end_date}"
            )

        db_obj = Absence(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_absences_by_employee(self, db: Session, employee_id: int):
        """Lấy danh sách đơn nghỉ của một nhân viên"""
        return db.query(Absence).filter(Absence.employee_id == employee_id).all()
    
    def delete_pending_absence(self, db: Session, absence_id: int, empId: int):
        """Xóa đơn nghỉ phép (Chỉ cho phép khi đang PENDING và đúng chủ sở hữu)"""
        
        db_obj = db.query(Absence).filter(
            Absence.id == absence_id,
            Absence.employee_id == empId
        ).first()
        
        if not db_obj:
            raise HTTPException(
                status_code=404, 
                detail="Không tìm thấy đơn nghỉ phép hoặc bạn không có quyền xóa đơn này"
            )

        if db_obj.status != ApprovalStatus.PENDING:
            raise HTTPException(
                status_code=400, 
                detail=f"Không thể xóa đơn vì trạng thái hiện tại là: {db_obj.status.value}"
            )

        db.delete(db_obj)
        db.commit()
        
        return {"id": absence_id}

    def approve_absence(self, db: Session, absence_id: int, obj_in: AbsenceApprove):
        """Duyệt hoặc từ chối đơn nghỉ phép và gửi thông báo cho nhân viên"""
        db_obj = db.query(Absence).filter(Absence.id == absence_id).first()
        
        if not db_obj:
            raise HTTPException(status_code=404, detail="Không tìm thấy đơn nghỉ phép")

        if db_obj.status != ApprovalStatus.PENDING:
            raise HTTPException(
                status_code=400, 
                detail=f"Đơn này đã được xử lý (Trạng thái: {db_obj.status.value})"
            )

        # Cập nhật trạng thái và note
        db_obj.status = obj_in.status
        if obj_in.note:
            db_obj.reason = (db_obj.reason or "") + f" | Note: {obj_in.note}"

        # Xử lý thông báo (Notification)
        notif_title = ""
        notif_content = ""
        notif_type = ""

        if obj_in.status == ApprovalStatus.APPROVED:
            notif_title = "Đơn nghỉ phép đã được duyệt!"
            notif_content = f"Đơn nghỉ từ {db_obj.start_date} đến {db_obj.end_date} của bạn đã được chấp thuận."
            notif_type = "ABSENCE_APPROVED"
        
        elif obj_in.status == ApprovalStatus.REJECTED:
            notif_title = "Đơn nghỉ phép bị từ chối"
            notif_content = f"Đơn nghỉ của bạn không được duyệt. Lý do: {obj_in.note or 'Không có lý do cụ thể'}"
            notif_type = "ABSENCE_REJECTED"

        if notif_title:
            new_notification = Notification(
                employee_id=db_obj.employee_id,
                title=notif_title,
                content=notif_content,
                notification_type=notif_type
            )
            db.add(new_notification)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_long_term_absence(self, db: Session, obj_in: LongTermAbsenceCreate):
        """
        Mặc định APPROVED vì do Admin/Hệ thống tạo.
        """
        db_absence = Absence(
            employee_id=obj_in.employee_id,
            absence_type_id=obj_in.absence_type_id,
            start_date=obj_in.start_date,
            end_date=obj_in.end_date,
            reason=obj_in.reason,
            status=ApprovalStatus.APPROVED,
        )
        
        db.add(db_absence)
        db.commit()
        db.refresh(db_absence)
        
        return db_absence

absence_service = AbsenceService()