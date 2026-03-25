from sqlalchemy.orm import Session
from app.models.vacation import Vacation
from app.schemas.vacation import VacationCreate, VacationUpdate
from fastapi import HTTPException

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