from datetime import date, timedelta

from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.vacation import Vacation
from app.schemas.vacation import VacationCreate, VacationUpdate

class CalendarService:
    def create_vacation(self, db: Session, obj_in: VacationCreate):
        if obj_in.end_date < obj_in.start_date:
            raise HTTPException(status_code=400, detail="Ngày kết thúc không được trước ngày bắt đầu")
        
        db_obj = Vacation(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_vacation(self, db: Session, vacation_id: int, obj_in: VacationUpdate):
        db_obj = db.query(Vacation).filter(Vacation.id == vacation_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Không tìm thấy ngày nghỉ")
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_vacation(self, db: Session, vacation_id: int):
        db_obj = db.query(Vacation).filter(Vacation.id == vacation_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Không tìm thấy ngày nghỉ")
        db.delete(db_obj)
        db.commit()
        return {"message": "Xóa thành công"}
        
    def get_vacations(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Vacation).offset(skip).limit(limit).all()
    
    def get_vacation_by_id(self, db: Session, vacation_id: int):
        vacation = db.query(Vacation).filter(Vacation.id == vacation_id).first()
        if not vacation:
            raise HTTPException(status_code=404, detail="Không tìm thấy ngày nghỉ này")
        return vacation
    
    def get_working_days_list(self, db: Session, start: date, end: date):
        days = []
        curr = start
        while curr <= end:
            if curr.weekday() < 5:
                is_holiday = db.query(Vacation).filter(
                    or_(
                        # TH1: Ngày nghỉ cố định (is_recurring = False)
                        and_(
                            Vacation.is_recurring == False,
                            Vacation.start_date <= curr,
                            Vacation.end_date >= curr
                        ),
                        # TH2: Ngày lễ lặp lại hàng năm (is_recurring = True)
                        # So sánh Tháng và Ngày, bỏ qua Năm
                        and_(
                            Vacation.is_recurring == True,
  
                            func.date_format(Vacation.start_date, '%m-%d') <= curr.strftime('%m-%d'),
                            func.date_format(Vacation.end_date, '%m-%d') >= curr.strftime('%m-%d')
                        )
                    )
                ).first()

                if not is_holiday:
                    days.append(curr)

            curr += timedelta(days=1)
        return days

calendar_service = CalendarService()