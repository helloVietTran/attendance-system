from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException

from app.models.vacation import Vacation
from app.schemas.vacation import VacationCreate, VacationUpdate
from app.models.employee import Employee
from app.models.absence import Absence, ApprovalStatus
from app.schemas.absence import AbsenceApprove, AbsenceCreate
from app.models.notification import Notification

class CalendarService:
    @staticmethod
    def create_vacation(db: Session, obj_in: VacationCreate):
        if obj_in.end_date < obj_in.start_date:
            raise HTTPException(status_code=400, detail="Ngày kết thúc không được trước ngày bắt đầu")
        
        db_obj = Vacation(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update_vacation(db: Session, vacation_id: int, obj_in: VacationUpdate):
        db_obj = db.query(Vacation).filter(Vacation.id == vacation_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Không tìm thấy ngày nghỉ")
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete_vacation(db: Session, vacation_id: int):
        db_obj = db.query(Vacation).filter(Vacation.id == vacation_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Không tìm thấy ngày nghỉ")
        db.delete(db_obj)
        db.commit()
        return {"message": "Xóa thành công"}
        
    @staticmethod
    def get_vacations(db: Session, skip: int = 0, limit: int = 100): # Đã xóa self
        """Lấy danh sách ngày nghỉ có phân trang"""
        return db.query(Vacation).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_vacation_by_id(db: Session, vacation_id: int): # Đã xóa self
        """Lấy chi tiết một ngày nghỉ cụ thể"""
        return db.query(Vacation).filter(Vacation.id == vacation_id).first()
    
    @staticmethod
    def create_absence(db: Session, obj_in: AbsenceCreate):
        emp = db.query(Employee).filter(Employee.id == obj_in.employee_id).first()
        if not emp:
            raise HTTPException(status_code=404, detail="Nhân viên không tồn tại")
            
        if obj_in.end_date < obj_in.start_date:
            raise HTTPException(status_code=400, detail="Ngày kết thúc không hợp lệ")

        overlap_check = db.query(Absence).filter(
            Absence.employee_id == obj_in.employee_id,
            # Trạng thái REJECTED thì không tính là đã tạo ngày nghỉ
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

    @staticmethod
    def get_absences_by_employee(db: Session, employee_id: int):
        return db.query(Absence).filter(Absence.employee_id == employee_id).all()
    
    @staticmethod
    def delete_pending_absence(db: Session, absence_id: int):
        db_obj = db.query(Absence).filter(Absence.id == absence_id).first()
        
        if not db_obj:
            raise HTTPException(status_code=404, detail="Không tìm thấy đơn nghỉ phép")

        # Chỉ cho phép xóa nếu đang ở trạng thái PENDING
        if db_obj.status != ApprovalStatus.PENDING:
            raise HTTPException(
                status_code=400, 
                detail=f"Không thể xóa đơn này vì nó đã ở trạng thái: {db_obj.status.value}"
            )

        db.delete(db_obj)
        db.commit()
        
        return {"message": "Đã xóa đơn nghỉ phép thành công", "id": absence_id}

    @staticmethod
    def approve_absence(db: Session, absence_id: int, obj_in: AbsenceApprove):
        db_obj = db.query(Absence).filter(Absence.id == absence_id).first()
        
        if not db_obj:
            raise HTTPException(status_code=404, detail="Không tìm thấy đơn nghỉ phép")

        # chỉ duyệt/từ chối khi đơn đang ở trạng thái PENDING
        if db_obj.status != ApprovalStatus.PENDING:
            raise HTTPException(
                status_code=400, 
                detail=f"Đơn này đã được xử lý trước đó (Trạng thái hiện tại: {db_obj.status.value})"
            )

        db_obj.status = obj_in.status
        if obj_in.note:
            db_obj.reason = (db_obj.reason or "") + f" | Note từ quản lý: {obj_in.note}"

        # Tạo thông báo
        if obj_in.status == ApprovalStatus.APPROVED:
            new_notification = Notification(
                employee_id=db_obj.employee_id,
                title="Đơn nghỉ phép đã được duyệt!",
                content=f"Đơn nghỉ từ ngày {db_obj.start_date} đến {db_obj.end_date} của bạn đã được chấp thuận.",
                notification_type="ABSENCE_APPROVED"
            )
            db.add(new_notification)
        
        elif obj_in.status == ApprovalStatus.REJECTED:
            new_notification = Notification(
                employee_id=db_obj.employee_id,
                title="Đơn nghỉ phép bị từ chối",
                content=f"Rất tiếc, đơn nghỉ của bạn không được duyệt. Lý do: {obj_in.note or 'Không có lý do cụ thể'}",
                notification_type="ABSENCE_REJECTED"
            )
        db.add(new_notification)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj